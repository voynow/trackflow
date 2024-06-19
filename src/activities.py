import os
from datetime import datetime, timedelta

import auth_manager as auth_manager
import polars as pl
from dotenv import load_dotenv

load_dotenv()


def activities_to_df(activities):
    df_schema = {
        "id": pl.UInt64,
        "name": pl.Utf8,
        "distance": pl.Float64,
        "moving_time": pl.Duration,
        "total_elevation_gain": pl.Float64,
        "start_date_local": pl.Datetime,
    }
    df_builder = {}

    for activity in activities:
        for attribute in df_schema:
            if attribute not in df_builder:
                df_builder[attribute] = []
            if activity.sport_type == "Run":
                df_builder[attribute].append(getattr(activity, attribute))

    return pl.DataFrame(
        {col: pl.Series(df_builder[col], dtype=df_schema[col]) for col in df_schema}
    )


def clean_activities_df(df):

    # sort ascending by start_date_local
    df = df.sort("start_date_local", descending=True)

    # convert distance from meters to miles
    # convert total_elevation_gain from meters to feet
    df = df.with_columns(
        [
            (pl.col("distance") / 1609.34).alias("distance_in_miles"),
            (pl.col("total_elevation_gain") * 3.28084).alias("elevation_gain_in_feet"),
        ]
    )

    # convert moving_time from milliseconds to minutes
    df = df.with_columns((pl.col("moving_time") / 60_000_000))

    # delete the original columns
    df = df.drop(["distance", "total_elevation_gain"])

    # add a column for pace
    df = df.with_columns(
        (pl.col("moving_time") / pl.col("distance_in_miles")).alias(
            "pace_minutes_per_mile"
        )
    )

    return df


def get_activities_df(athlete_id):

    user_auth = auth_manager.authenticate_athlete(athlete_id)
    strava_client = auth_manager.get_configured_strava_client(user_auth)
    timedelta_6_weeks = datetime.now() - timedelta(weeks=7)
    activities = strava_client.get_activities(after=timedelta_6_weeks)

    df = activities_to_df(activities)
    df = clean_activities_df(df)

    return df


def get_week_nums(df):

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


def agg_by_week(df):
    df = df.groupby("week_num").agg(
        [
            pl.sum("distance_in_miles").round(2).alias("total_distance_miles"),
            pl.mean("distance_in_miles").round(2).alias("avg_distance_miles"),
            pl.mean("elevation_gain_in_feet").round(2).alias("avg_elevation_gain_feet"),
            pl.mean("pace_minutes_per_mile")
            .round(2)
            .alias("avg_pace_minutes_per_mile"),
        ]
    )

    return df.sort("week_num", descending=False)


def get_pct_change(df):
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


def group_by_weeks(df):
    df = get_week_nums(df)
    df = agg_by_week(df)
    df = get_pct_change(df)

    # sort for chronological order and remove final null percent change row
    return df.sort("week_num", descending=True)[:-1]
