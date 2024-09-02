from datetime import datetime, timedelta
from typing import Dict, List

import polars as pl
from dotenv import load_dotenv
from stravalib.client import Client
from stravalib.model import Activity

from src.types.activity_summary import ActivitySummary
from src.types.day_of_week_summary import DayOfWeekSummary
from src.types.week_summary import WeekSummary
from src.utils import datetime_now_est

load_dotenv()


def activities_to_df(activities: List[Activity]) -> pl.DataFrame:
    """
    Converts a list of activities into polars DataFrame

    :param activities: List of activity objects to be converted to DataFrame
    :return: A polars DataFrame with activities data
    """
    df_schema = {
        "id": pl.UInt64,
        "name": pl.Utf8,
        "distance": pl.Float64,
        "moving_time": pl.Duration,
        "total_elevation_gain": pl.Float64,
        "start_date_local": pl.Datetime,
    }
    df_builder: Dict[str, List] = {}

    for activity in activities:
        for attribute in df_schema:
            if attribute not in df_builder:
                df_builder[attribute] = []
            if activity.sport_type == "Run":
                df_builder[attribute].append(getattr(activity, attribute))

    return pl.DataFrame(
        {col: pl.Series(df_builder[col], dtype=df_schema[col]) for col in df_schema}
    )


def add_missing_dates(
    df: pl.DataFrame, start_date: datetime, end_date: datetime
) -> pl.DataFrame:
    """
    Ensures that the DataFrame contains all dates between the start and end date

    :param df: The initial polars DataFrame containing activity data
    :param start_date: The start date of the range
    :param end_date: The end date of the range
    """
    df_with_date = df.with_columns(df["start_date_local"].dt.date().alias("date")).drop(
        "start_date_local"
    )
    n_days = (end_date.date() - start_date.date()).days + 1
    date_range_df = pl.DataFrame(
        {"date": [start_date.date() + timedelta(days=i) for i in range(n_days)]}
    )
    return date_range_df.join(df_with_date, on="date", how="left")


def preprocess(df: pl.DataFrame) -> pl.DataFrame:
    """
    :param df: The initial polars DataFrame containing activity data
    :return: A transformed polars DataFrame with cleansed data
    """
    METERS_PER_MILE = 1609.34
    FEET_PER_METER = 3.28084
    MICROSECONDS_PER_MINUTE = 1_000_000 * 60

    # Define transformation operations for each column
    col_operations = [
        pl.col("date")
        .dt.strftime("%a")
        .str.to_lowercase()
        .first()
        .alias("day_of_week"),
        pl.col("date").dt.week().first().alias("week_of_year"),
        pl.col("date").dt.year().first().alias("year"),
        pl.col("distance").sum().alias("distance_in_miles") / METERS_PER_MILE,
        pl.col("total_elevation_gain").sum().alias("elevation_gain_in_feet")
        * FEET_PER_METER,
        (pl.col("moving_time").sum() / MICROSECONDS_PER_MINUTE).alias(
            "moving_time_in_minutes"
        ),
        (
            (pl.col("moving_time").sum() / MICROSECONDS_PER_MINUTE)
            / (pl.col("distance").sum() / METERS_PER_MILE)
        ).alias("pace_minutes_per_mile"),
    ]

    # Apply transformations, sorting, column removals, and filtering
    return (
        df.groupby("date")
        .agg(col_operations)
        .sort("date")
        # drop incomplete first week
        .filter(pl.col("week_of_year") != pl.col("week_of_year").min())
    )


def get_activities_df(strava_client: Client, num_weeks: int = 8) -> pl.DataFrame:
    """
    Fetches activities for a given athlete ID and returns a DataFrame with daily aggregated activities

    :param strava_client: The Strava client object to fetch data.
    :param num_weeks: The number of weeks to fetch activities for.
    :return: A cleaned and processed DataFrame of the athlete's daily aggregated activities.
    """
    end_date = datetime_now_est()
    start_date = end_date - timedelta(weeks=num_weeks)

    activities = strava_client.get_activities(after=start_date, before=end_date)
    raw_df = activities_to_df(activities)
    all_dates_df = add_missing_dates(
        df=raw_df, start_date=start_date, end_date=end_date
    )
    return preprocess(all_dates_df)


def get_activity_summaries(strava_client, num_weeks=8) -> List[ActivitySummary]:
    """
    Fetches and returns activity summaries for a given athlete ID

    :param athlete_id: The Strava athlete ID
    :param num_weeks: The number of weeks to fetch activities for
    :return: A list of ActivitySummary objects, lighter weight than the full get_activities_df DataFrame
    """
    df = get_activities_df(strava_client, num_weeks)
    concise_activities_df = df.with_columns(
        pl.col("date").apply(
            lambda x: x.strftime("%A, %B %d, %Y"), return_dtype=pl.Utf8
        ),
        pl.col("distance_in_miles").apply(lambda x: round(x, 2)),
        pl.col("elevation_gain_in_feet").apply(lambda x: round(x, 2)),
        pl.col("pace_minutes_per_mile").apply(lambda x: round(x, 2)),
    ).drop(
        "id",
        "name",
        "day_of_week",
        "week_of_year",
        "year",
        "moving_time_in_minutes",
    )
    return [ActivitySummary(**row) for row in concise_activities_df.rows(named=True)]


def get_day_of_week_summaries(activities_df: pl.DataFrame) -> List[DayOfWeekSummary]:
    """
    Aggregate activities DataFrame by day of the week and calculate summary statistics
    for each day. The resulting objects provide insights into the average week of
    the athlete from a day-of-week perspective.

    :param activities_df: The DataFrame containing activities data
    :return: A list of DayOfWeekSummary objects with summary statistics
    """
    day_of_week_order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    df = (
        activities_df.groupby("day_of_week")
        .agg(
            [
                pl.when(pl.col("distance_in_miles") > 0.25)
                .then(pl.lit(1))
                .otherwise(pl.lit(0))
                .sum()
                .alias("number_of_runs"),
                pl.col("distance_in_miles").mean().alias("avg_miles"),
                pl.col("pace_minutes_per_mile").drop_nans().mean().alias("avg_pace"),
            ]
        )
        .with_columns(
            pl.col("day_of_week")
            .apply(lambda x: day_of_week_order.index(x))
            .alias("day_order")
        )
        .sort("day_order")
        .drop("day_order")
    )

    return [
        DayOfWeekSummary(
            day_of_week=row["day_of_week"],
            number_of_runs=row["number_of_runs"],
            avg_miles=round(row["avg_miles"], 2),
            avg_pace=round(row["avg_pace"], 2) if row["avg_pace"] is not None else 0,
        )
        for row in df.to_dicts()
    ]


def get_weekly_summaries(activities_df: pl.DataFrame) -> List[WeekSummary]:
    """
    Aggregate activities DataFrame by week of the year and calculate
    load for each week

    :param activities_df: The DataFrame containing activities data
    :return: A list of WeekSummary objects with summary statistics
    """
    df = (
        activities_df.groupby(["year", "week_of_year"])
        .agg(
            [
                pl.col("distance_in_miles").sum().alias("total_distance"),
                pl.col("distance_in_miles").max().alias("longest_run"),
            ]
        )
        .sort(["year", "week_of_year"])
    )

    return [
        WeekSummary(
            year=row["year"],
            week_of_year=row["week_of_year"],
            longest_run=round(row["longest_run"], 2),
            total_distance=round(row["total_distance"], 2),
        )
        for row in df.to_dicts()
    ]
