import os
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict

from stravalib.client import Client

from src.activities import (
    get_activities_df,
    get_activity_summaries,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.auth_manager import get_strava_client
from src.constants import COACH_ROLE
from src.email_manager import (
    send_email,
    training_week_to_html,
    training_week_update_to_html,
)
from src.supabase_client import (
    get_training_week_with_coaching,
    list_users,
    upsert_training_week_update,
    upsert_training_week_with_coaching,
)
from src.training_week import generate_training_week
from src.training_week_update import get_updated_training_week
from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import TrainingWeekWithPlanning
from src.types.user_row import UserRow


def get_athlete_full_name(strava_client) -> str:
    athlete = strava_client.get_athlete()
    return f"{athlete.firstname} {athlete.lastname}"


def run_weekly_update_process(
    user: UserRow,
    upsert_fn: Callable[[str, TrainingWeekWithPlanning], None],
    email_fn: Callable[[Dict[str, str], str, str], None],
) -> None:
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
    strava_client = get_strava_client(user.athlete_id)

    activities_df = get_activities_df(strava_client)
    day_of_week_summaries = get_day_of_week_summaries(activities_df)
    weekly_summaries = get_weekly_summaries(activities_df)
    training_week_with_coaching = generate_training_week(
        sysmsg_base=sysmsg_base,
        weekly_summaries=weekly_summaries,
        day_of_week_summaries=day_of_week_summaries,
    )

    upsert_fn(user.athlete_id, training_week_with_coaching)
    email_fn(
        to={"email": user.email, "name": get_athlete_full_name(strava_client)},
        subject="Training Schedule Just Dropped 🏃",
        html_content=training_week_to_html(training_week_with_coaching),
    )


def run_mid_week_update_process(
    user: UserRow,
    upsert_fn: Callable[[str, MidWeekAnalysis, TrainingWeekWithPlanning], None],
    email_fn: Callable[[Dict[str, str], str, str], None],
) -> None:
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
    strava_client = get_strava_client(user.athlete_id)

    training_week_with_coaching = get_training_week_with_coaching(user.athlete_id)
    current_weeks_activity_summaries = get_activity_summaries(
        strava_client, num_weeks=1
    )
    mid_week_analysis = MidWeekAnalysis(
        activities=current_weeks_activity_summaries,
        training_week=training_week_with_coaching.training_week,
    )
    training_week_update_with_planning = get_updated_training_week(
        sysmsg_base=sysmsg_base, mid_week_analysis=mid_week_analysis
    )

    upsert_fn(user.athlete_id, mid_week_analysis, training_week_update_with_planning)
    email_fn(
        to={"email": user.email, "name": get_athlete_full_name(strava_client)},
        subject="Training Schedule Update 🏃",
        html_content=training_week_update_to_html(
            mid_week_analysis=mid_week_analysis,
            training_week_update_with_planning=training_week_update_with_planning,
        ),
    )


def core_executor(user: UserRow) -> None:
    """
    On sundays, generate a new training week, otherwise update the current training week
    """
    # get current time in EST
    est = timezone(timedelta(hours=-5))
    datetime_now_est = datetime.now(tz=timezone.utc).astimezone(est)

    # day 6 is Sunday
    if datetime_now_est.weekday() == 6:
        run_weekly_update_process(
            user=user,
            upsert_fn=upsert_training_week_with_coaching,
            email_fn=send_email,
        )
    else:
        run_mid_week_update_process(
            user=user,
            upsert_fn=upsert_training_week_update,
            email_fn=send_email,
        )


def lambda_handler(event, context):
    """Main entry point for production workload"""
    [core_executor(user) for user in list_users()]
