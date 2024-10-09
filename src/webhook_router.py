import os

from src import auth_manager
from src.supabase_client import (
    get_user,
)
from src.types.update_pipeline import ExeType
from src.update_pipeline import training_week_update_executor


def handle_activity_create(user, event):
    strava_client = auth_manager.get_strava_client(user.athlete_id)
    activity = strava_client.get_activity(event.get("object_id"))

    if activity.sport_type == "Run":
        return training_week_update_executor(user, ExeType.MID_WEEK)

    return {"success": False, "error": "Unsupported activity type"}


def handle_request(event: dict) -> dict:
    """
    Handle Strava webhook events for activities and athletes.

    :param event: Webhook event payload from Strava
    :return: dict with {"success": bool, "message": str (optional)}
    """
    if int(event.get("subscription_id")) != int(
        os.environ["STRAVA_WEBHOOK_SUBSCRIPTION_ID"]
    ):
        return {"success": False, "error": "Invalid subscription ID"}

    user = get_user(event.get("owner_id"))
    event_type = event.get("object_type")
    aspect_type = event.get("aspect_type")

    if event_type == "activity":
        if aspect_type == "create":
            return handle_activity_create(user, event)
        if aspect_type in {"update", "delete"}:
            return {
                "success": True,
                "message": f"Activity {event.get('object_id')} {aspect_type}d",
            }

    return {"success": False, "error": "Unknown event type"}
