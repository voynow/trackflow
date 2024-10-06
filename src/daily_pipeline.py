import logging
import traceback
from typing import Callable, Dict, Optional

from openai import APIResponse
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
    send_alert_email,
    send_email,
    training_week_to_html,
)
from src.mid_week_update import generate_mid_week_update
from src.new_training_week import generate_new_training_week
from src.supabase_client import (
    get_training_week,
    get_training_week_test,
    upsert_training_week,
)
from src.types.training_week import TrainingWeek
from src.types.user_row import UserRow
from src.utils import datetime_now_est

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def daily_generic_pipeline(
    user: UserRow,
    pipeline_function: Callable[[UserRow, Client], TrainingWeek],
    email_subject: str = "TrackFlow 🏃‍♂️🎯",
    upsert_training_week: Callable[
        [int, TrainingWeek], APIResponse
    ] = upsert_training_week,
    send_email: Callable[[Dict[str, str], str, str], None] = send_email,
) -> TrainingWeek:
    """General processing for training week updates."""
    strava_client = get_strava_client(user.athlete_id)
    athlete = strava_client.get_athlete()
    training_week = pipeline_function(user=user, strava_client=strava_client)

    upsert_training_week(user.athlete_id, training_week)
    send_email(
        to={"email": user.email, "name": f"{athlete.firstname} {athlete.lastname}"},
        subject=email_subject,
        html_content=training_week_to_html(training_week),
    )
    return training_week


def new_training_week_pipeline(
    user: UserRow,
    strava_client: Client,
) -> TrainingWeek:
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
    activities_df = get_activities_df(strava_client)
    day_of_week_summaries = get_day_of_week_summaries(activities_df)
    weekly_summaries = get_weekly_summaries(activities_df)
    return generate_new_training_week(
        sysmsg_base=sysmsg_base,
        weekly_summaries=weekly_summaries,
        day_of_week_summaries=day_of_week_summaries,
    )


def mid_week_update_pipeline(
    user: UserRow,
    strava_client: Client,
    get_training_week: Callable[[int], TrainingWeek] = get_training_week,
) -> TrainingWeek:
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
    training_week = get_training_week(user.athlete_id)
    completed_activities = get_activity_summaries(strava_client, num_weeks=1)
    return generate_mid_week_update(
        sysmsg_base=sysmsg_base,
        training_week=training_week,
        completed_activities=completed_activities,
    )


def mid_week_update_pipeline_test(
    user: UserRow,
    strava_client: Client,
) -> TrainingWeek:
    return mid_week_update_pipeline(
        user=user,
        strava_client=strava_client,
        get_training_week=get_training_week_test,
    )


def daily_executor(user: UserRow) -> dict:
    """Decides between generating a new week or updating based on the day."""
    try:
        # Sunday is day 6
        if datetime_now_est().weekday() == 6:
            daily_generic_pipeline(
                user=user,
                pipeline_function=new_training_week_pipeline,
                email_subject="Training Schedule Just Dropped 🏃‍♂️🎯",
            )
        else:
            daily_generic_pipeline(
                user=user,
                pipeline_function=mid_week_update_pipeline,
                email_subject="www.trackflow.xyz is live! 🏃‍♂️🎯",
            )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error processing user {user.athlete_id}: {e}")
        send_alert_email(
            subject="TrackFlow Alert: Error in Lambda Function",
            text_content=f"Error for {user.email=} {e} with traceback: {traceback.format_exc()}",
        )
        return {"success": False, "error": str(e)}
