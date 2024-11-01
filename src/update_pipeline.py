import logging
import os
import traceback
from typing import Callable, Literal, TypeAlias

from openai import APIResponse
from stravalib.client import Client

from src.activities import (
    get_activities_df,
    get_activity_summaries,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.apn import send_push_notif_wrapper
from src.auth_manager import get_strava_client
from src.constants import COACH_ROLE
from src.email_manager import send_alert_email
from src.mid_week_update import generate_mid_week_update
from src.new_training_week import generate_new_training_week
from src.supabase_client import (
    get_training_week,
    has_user_updated_today,
    list_users,
    upsert_training_week,
)
from src.types.update_pipeline import ExeType
from src.types.user_row import UserRow
from src.utils import datetime_now_est

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_training_week(user: UserRow, exe_type: ExeType) -> dict:
    """Single function to handle all training week updates"""
    try:
        strava_client = get_strava_client(user.athlete_id)

        if exe_type == ExeType.NEW_WEEK:
            activities_df = get_activities_df(strava_client)
            day_summaries = get_day_of_week_summaries(activities_df)
            weekly_summaries = get_weekly_summaries(activities_df)
            training_week = generate_new_training_week(
                sysmsg_base=f"{COACH_ROLE}\n{user.preferences}",
                weekly_summaries=weekly_summaries,
                day_of_week_summaries=day_summaries,
            )
        else:  # ExeType.MID_WEEK
            current_week = get_training_week(user.athlete_id)
            activities = get_activity_summaries(strava_client, num_weeks=1)
            training_week = generate_mid_week_update(
                sysmsg_base=f"{COACH_ROLE}\n{user.preferences}",
                training_week=current_week,
                completed_activities=activities,
            )

        upsert_training_week(user.athlete_id, training_week)
        send_push_notif_wrapper(user)
        return {"success": True}

    except Exception as e:
        logger.error(f"Error processing user {user.athlete_id}: {str(e)}")
        send_alert_email(
            subject="TrackFlow Alert: Update Error",
            text_content=f"Error processing user {user.athlete_id}: {str(e)}\n{traceback.format_exc()}",
        )
        return {"success": False, "error": str(e)}


def nightly_trigger_orchestrator() -> dict:
    """
    Evenings excluding Sunday: Send update to users who have not yet triggered an update today
    Sunday evening: Send new training week to all active users
    """
    if datetime_now_est().weekday() != 6:
        for user in list_users():
            if not has_user_updated_today(user.athlete_id):
                update_training_week(user, ExeType.MID_WEEK)
    else:
        for user in list_users():
            update_training_week(user, ExeType.NEW_WEEK)
    return {"success": True}
