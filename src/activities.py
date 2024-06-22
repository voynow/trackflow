import os
from datetime import datetime, timedelta
from typing import Dict, List

import auth_manager
import polars as pl
from dotenv import load_dotenv
from stravalib.model import Activity

load_dotenv()


def activities_to_df(activities: List[Activity]) -> pl.DataFrame:
    """
    Converts a list of activities into a polars DataFrame according to a
    predefined schema

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


def clean_activities_df(df: pl.DataFrame) -> pl.DataFrame:
    """
    Cleans and transforms the activities DataFrame by sorting, converting units,
    and adding derived columns

    :param df: The initial polars DataFrame containing activity data
    :return: A transformed polars DataFrame with cleansed data
    """
    df = df.sort("start_date_local", descending=True)
    df = df.with_columns(
        [
            (pl.col("distance") / 1609.34).alias("distance_in_miles"),
            (pl.col("total_elevation_gain") * 3.28084).alias("elevation_gain_in_feet"),
            (pl.col("moving_time") / 60_000_000).alias("moving_time_in_minutes"),
        ]
    )

    df = df.with_columns(
        (pl.col("moving_time_in_minutes") / pl.col("distance_in_miles")).alias(
            "pace_minutes_per_mile"
        )
    )
    df = df.drop(["distance", "total_elevation_gain", "moving_time"])
    return df


def get_activities_df(athlete_id: str) -> pl.DataFrame:
    """
    Fetches and returns activities data for a given athlete ID as a DataFrame,
    cleansed and processed

    :param athlete_id: The Strava athlete ID
    :return: A cleaned and processed DataFrame of the athlete's activities
    """
    user_auth = auth_manager.authenticate_athlete(athlete_id)
    strava_client = auth_manager.get_configured_strava_client(user_auth)
    timedelta_6_weeks = datetime.now() - timedelta(weeks=7)
    activities = strava_client.get_activities(after=timedelta_6_weeks)

    df = activities_to_df(activities)
    df = clean_activities_df(df)
    return df


def get_week_nums(df: pl.DataFrame) -> pl.DataFrame:
    """
    Adds a 'week_num' column to the DataFrame based on the 'start_date_local'
    date

    :param df: The DataFrame with activities data
    :return: DataFrame with an additional 'week_num' column
    """
    current_date = datetime.now().date()
    min_date = pl.lit(current_date - timedelta(weeks=7))
    max_date = pl.lit(current_date)
    date_range = max_date - min_date
    interval = date_range / 7

    df = df.with_columns(pl.col("start_date_local").cast(pl.Date).alias("date"))
    df = df.with_columns(
        (((pl.col("date") - min_date) / interval).floor().cast(pl.UInt32)).alias(
            "week_num"
        )
    )
    return df


def agg_by_week(df: pl.DataFrame) -> pl.DataFrame:
    """
    Aggregates activities data by week, calculating total and average distances,
    average elevation gain, and pace

    :param df: The DataFrame with 'week_num' assigned
    :return: Aggregated DataFrame by week
    """
    df = df.groupby("week_num").agg(
        [
            pl.count("id").alias("num_runs"),
            pl.sum("distance_in_miles").round(2).alias("total_distance_miles"),
            pl.sum("moving_time_in_minutes").round(2).alias("total_moving_time_minutes"),
            pl.sum("elevation_gain_in_feet").round(2).alias("total_elevation_gain_feet"),
        ]
    )

    df = df.with_columns(
        (pl.col("total_moving_time_minutes") / pl.col("total_distance_miles")).round(2).alias(
            "avg_pace_minutes_per_mile"
        ),
    )

    return df.sort("week_num", descending=False)


def get_pct_change(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calculates the percentage change in total distance between weeks

    :param df: The DataFrame containing weekly aggregated data
    :return: DataFrame with the percentage change added as a column
    """
    df = df.with_columns(
        (
            (pl.col("total_distance_miles") - pl.col("total_distance_miles").shift(1))
            / pl.col("total_distance_miles").shift(1)
            * 100
        ).alias("percent_change_total_miles")
    )
    df = df.with_columns(
        pl.when(pl.col("percent_change_total_miles").is_finite())
        .then(pl.col("percent_change_total_miles"))
        .otherwise(None)
        .alias("percent_change_total_miles")
    )
    return df


def group_by_weeks(df: pl.DataFrame) -> pl.DataFrame:
    """
    Processes the given DataFrame to group activities by week, aggregate them,
    and calculate percentage changes

    :param df: DataFrame with activities data
    :return: Processed DataFrame grouped by weeks with percentage changes
    """
    return (
        df.pipe(get_week_nums)
        .pipe(agg_by_week)
        .pipe(get_pct_change)
        .sort("week_num", descending=True)[:-1]
    )
