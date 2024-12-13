from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional

from src import constants
from src.types.activity import Activity, ActivitySummary, DailyMetrics, WeekSummary
from src.utils import datetime_now_est, round_all_floats
from stravalib.client import Client


def add_missing_dates(
    activities: List[Activity], start_date: datetime, end_date: datetime
) -> List[Activity]:
    """
    Ensures that the list of activities includes placeholder activities for all dates
    between the start and end date.

    :param activities: List of Activity Pydantic models.
    :param start_date: The start date of the range.
    :param end_date: The end date of the range.
    :return: A list of Activity objects, with missing dates filled in as placeholder activities.
    """
    existing_dates = {activity.start_date_local.date() for activity in activities}
    total_days = (end_date.date() - start_date.date()).days + 1
    all_dates = {start_date.date() + timedelta(days=i) for i in range(total_days)}
    missing_dates = all_dates - existing_dates

    placeholders = [
        Activity(
            start_date=datetime.combine(date, datetime.min.time()),
            start_date_local=datetime.combine(date, datetime.min.time()),
        )
        for date in missing_dates
    ]
    return sorted(activities + placeholders, key=lambda x: x.start_date_local)


def aggregate_daily_metrics(activities: List[Activity]) -> List[DailyMetrics]:
    """
    Aggregates and transforms activity data to calculate daily and weekly metrics.

    :param activities: List of Activity Pydantic models containing activity data
    :return: A list of DailyMetrics objects with aggregated and transformed metrics
    """

    results = []
    activities_by_date = defaultdict(list)
    for activity in activities:
        activities_by_date[activity.start_date_local.date()].append(activity)

    for activity_date, daily_activities in activities_by_date.items():
        total_distance = sum(a.distance for a in daily_activities)
        total_elevation_gain = sum(a.total_elevation_gain for a in daily_activities)
        total_moving_time = sum(a.moving_time.total_seconds() for a in daily_activities)
        activity_count = len([a for a in daily_activities if a.id != -1])

        if total_distance > 0:
            pace_minutes_per_mile = (total_moving_time / 60) / (
                total_distance / constants.METERS_PER_MILE
            )
        else:
            pace_minutes_per_mile = None

        results.append(
            round_all_floats(
                DailyMetrics(
                    date=activity_date,
                    day_of_week=activity_date.strftime("%a").lower(),
                    week_of_year=activity_date.isocalendar()[1],
                    year=activity_date.year,
                    distance_in_miles=total_distance / constants.METERS_PER_MILE,
                    elevation_gain_in_feet=total_elevation_gain
                    * constants.FEET_PER_METER,
                    moving_time_in_minutes=total_moving_time / 60,
                    pace_minutes_per_mile=pace_minutes_per_mile,
                    activity_count=activity_count,
                )
            )
        )

    results = sorted(results, key=lambda x: x.date)
    first_week = min(item.week_of_year for item in results)
    results = [item for item in results if item.week_of_year != first_week]

    return results


def get_daily_activity(
    strava_client: Client, dt: datetime, num_weeks: int = 8
) -> List[DailyMetrics]:
    """
    Fetches activities for a given athlete ID and returns a DataFrame with daily aggregated activities

    :param strava_client: The Strava client object to fetch data.
    :param num_weeks: The number of weeks to fetch activities for.
    :return: A cleaned and processed DataFrame of the athlete's daily aggregated activities.
    """
    start_date = dt - timedelta(weeks=num_weeks)

    all_strava_activities = strava_client.get_activities(after=start_date, before=dt)

    # filter and convert to our Activity type
    activities = [
        Activity(**activity.__dict__)
        for activity in all_strava_activities
        if activity.sport_type == "Run"
    ]

    # add empty activities for missing dates
    all_dates_activities = add_missing_dates(
        activities=activities, start_date=start_date, end_date=dt
    )

    # aggregate metrics
    return aggregate_daily_metrics(all_dates_activities)


def get_weekly_summaries(
    strava_client: Optional[Client] = None,
    daily_metrics: Optional[List[DailyMetrics]] = None,
    dt: Optional[datetime] = None,
) -> List[WeekSummary]:
    """
    Aggregate daily metrics by week of the year and calculate load for each week.

    :param strava_client: The Strava client object to fetch data.
    :param daily_metrics: List of DailyMetrics objects
    :param dt: datetime injection, helpful for testing
    :return: A list of WeekSummary objects with summary statistics
    """
    if strava_client is None and daily_metrics is None:
        raise ValueError("Either strava_client or daily_metrics must be provided")

    if daily_metrics is None:
        daily_metrics = get_daily_activity(strava_client, dt=dt)

    weekly_aggregates = defaultdict(
        lambda: {"total_distance": 0, "longest_run": 0, "start_of_week": None}
    )

    for metrics in daily_metrics:
        key = (metrics.year, metrics.week_of_year)

        # calculate total distance and longest run
        weekly_aggregates[key]["total_distance"] += metrics.distance_in_miles
        weekly_aggregates[key]["longest_run"] = max(
            weekly_aggregates[key]["longest_run"], metrics.distance_in_miles
        )

        # update start of week
        if (
            weekly_aggregates[key]["start_of_week"] is None
            or metrics.date < weekly_aggregates[key]["start_of_week"]
        ):
            weekly_aggregates[key]["start_of_week"] = metrics.date

    weekly_summaries = [
        WeekSummary(
            year=year,
            week_of_year=week,
            week_start_date=start_of_week,
            longest_run=round(aggregate["longest_run"], 2),
            total_distance=round(aggregate["total_distance"], 2),
        )
        for (year, week), aggregate in sorted(weekly_aggregates.items())
        for start_of_week in [aggregate["start_of_week"]]
    ]

    return weekly_summaries
