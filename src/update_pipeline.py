import logging
import os
import traceback
from typing import Callable, Dict

from openai import APIResponse
from stravalib.client import Client

from src.activities import (
    get_activities_df,
    get_activity_summaries,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.apn import send_push_notification
from src.auth_manager import get_strava_client
from src.constants import COACH_ROLE
from src.email_manager import send_alert_email
from src.mid_week_update import generate_mid_week_update
from src.new_training_week import generate_new_training_week
from src.supabase_client import (
    get_training_week,
    get_training_week_test,
    get_user,
    get_user_auth,
    has_user_updated_today,
    list_users,
    upsert_training_week,
)
from src.types.training_week import TrainingWeek
from src.types.update_pipeline import ExeType
from src.types.user_row import UserRow
from src.utils import datetime_now_est

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def training_week_update_pipeline(
    user: UserRow,
    pipeline_function: Callable[[UserRow, Client], TrainingWeek],
    upsert_training_week: Callable[
        [int, TrainingWeek], APIResponse
    ] = upsert_training_week,
) -> TrainingWeek:
    """General processing for training week updates."""
    strava_client = get_strava_client(user.athlete_id)
    training_week = pipeline_function(user=user, strava_client=strava_client)
    upsert_training_week(user.athlete_id, training_week)

    user_auth = get_user_auth(user.athlete_id)
    if user_auth.device_token:
        send_push_notification(
            device_token=user_auth.device_token,
            title="TrackFlow 🏃‍♂️🎯",
            body="Your training week has been updated!",
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


def webhook_executor(user: UserRow) -> dict:
    """Silently updates db on every new activity"""
    training_week_update_pipeline(
        user=user,
        pipeline_function=mid_week_update_pipeline,
    )
    return {"success": True}


def training_week_update_executor(
    user: UserRow, exetype: ExeType, invocation_id: str = "manual-trigger"
) -> dict:
    """
    Decides between generating a new week or updating based on the day.
    Captures and logs full tracebacks for errors.
    """
    try:
        if exetype == ExeType.NEW_WEEK:
            training_week_update_pipeline(
                user=user,
                pipeline_function=new_training_week_pipeline,
            )
        elif exetype == ExeType.MID_WEEK:
            training_week_update_pipeline(
                user=user,
                pipeline_function=mid_week_update_pipeline,
            )
    except Exception as e:
        error_msg = f"{invocation_id=} | Error processing user {user.athlete_id} | {str(e)}\nTraceback: {traceback.format_exc()}"
        logger.error(error_msg)
        send_alert_email(
            subject="TrackFlow Alert: Error in lambda_handler",
            text_content=error_msg,
        )

        return {"success": False, "error": str(e)}

    return {"success": True}


def integration_test_executor(invocation_id: str) -> dict:
    """
    Run a full update pipeline for Jamies account
    """
    training_week_update_executor(
        user=get_user(os.environ["JAMIES_ATHLETE_ID"]),
        exetype=ExeType.MID_WEEK,
        invocation_id=invocation_id,
    )
    training_week_update_executor(
        user=get_user(os.environ["JAMIES_ATHLETE_ID"]),
        exetype=ExeType.NEW_WEEK,
        invocation_id=invocation_id,
    )
    return {"success": True}


def nightly_trigger_orchestrator(invocation_id: str) -> dict:
    """
    Evenings excluding Sunday: Send update to users who have not yet triggered an update today
    Sunday evening: Send new training week to all active users
    """
    if datetime_now_est().weekday() != 6:
        for user in list_users():
            if user.is_active and not has_user_updated_today(user.athlete_id):
                training_week_update_executor(
                    user=user,
                    exetype=ExeType.MID_WEEK,
                    invocation_id=invocation_id,
                )
    else:
        for user in list_users():
            if user.is_active:
                training_week_update_executor(
                    user=user,
                    exetype=ExeType.NEW_WEEK,
                    invocation_id=invocation_id,
                )
    return {"success": True}
