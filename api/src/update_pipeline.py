import logging
import traceback

from src.activities import (
    get_activity_summaries,
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
    upsert_training_week,
)
from src.types.update_pipeline import ExeType
from src.types.user import UserRow

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_training_week(user: UserRow, exe_type: ExeType) -> dict:
    """Single function to handle all training week updates"""
    try:
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

    except Exception as e:
        logger.error(f"Error processing user {user.athlete_id}: {str(e)}")
        send_alert_email(
            subject="TrackFlow Alert: Update Error",
            text_content=f"Error processing user {user.athlete_id}: {str(e)}\n{traceback.format_exc()}",
        )
        return {"success": False, "error": str(e)}
