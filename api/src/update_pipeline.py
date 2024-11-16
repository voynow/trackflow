import logging

from src.utils import datetime_now_est
from src.supabase_client import has_user_updated_today
from src.activities import (
    get_activity_summaries,
    get_weekly_summaries,
)
from src.apn import send_push_notif_wrapper
from src.auth_manager import get_strava_client
from src.constants import COACH_ROLE
from src.mid_week_update import generate_mid_week_update
from src.new_training_week import generate_new_training_week
from src.supabase_client import (
    get_training_week,
    list_users,
    upsert_training_week,
)
from src.types.update_pipeline import ExeType
from src.types.user import UserRow

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_training_week(user: UserRow, exe_type: ExeType) -> dict:
    """Single function to handle all training week updates"""
    strava_client = get_strava_client(user.athlete_id)

    if exe_type == ExeType.NEW_WEEK:
        weekly_summaries = get_weekly_summaries(strava_client)
        training_week = generate_new_training_week(
            sysmsg_base=f"{COACH_ROLE}\nClient Preferences: {user.preferences}",
            weekly_summaries=weekly_summaries,
        )
    else:  # ExeType.MID_WEEK
        current_week = get_training_week(user.athlete_id)
        activity_summaries = get_activity_summaries(strava_client, num_weeks=1)
        training_week = generate_mid_week_update(
            sysmsg_base=f"{COACH_ROLE}\nClient Preferences: {user.preferences}",
            training_week=current_week,
            completed_activities=activity_summaries,
        )

    upsert_training_week(user.athlete_id, training_week)
    send_push_notif_wrapper(user)
    return {"success": True}


def update_all_users() -> dict:
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