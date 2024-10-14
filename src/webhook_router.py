import json
import os

from src import auth_manager
from src.supabase_client import (
    get_user,
)
from src.types.update_pipeline import ExeType
from src.types.user_row import UserRow
from src.update_pipeline import training_week_update_executor


def is_strava_webhook_event(event: dict) -> bool:
    """
    Check if the event is a valid SQS event from Strava webhook

    :param event: The event dictionary containing event data
    :return: True if the event is a valid Strava webhook event, False otherwise
    """
    if not event.get("Records") or len(event.get("Records")) < 1:
        return False

    try:
        webhook_event = json.loads(event.get("Records")[0].get("body"))
    except json.JSONDecodeError:
        return False

    return (
        webhook_event.get("subscription_id")
        and webhook_event.get("aspect_type")
        and webhook_event.get("object_type")
        and webhook_event.get("object_id")
        and webhook_event.get("owner_id")
    )


def handle_activity_create(user: UserRow, event: dict, invocation_id: str) -> dict:
    strava_client = auth_manager.get_strava_client(user.athlete_id)
    activity = strava_client.get_activity(event.get("object_id"))

    if activity.sport_type == "Run":
        return training_week_update_executor(
            user=user,
            exetype=ExeType.MID_WEEK,
            invocation_id=invocation_id,
        )

    return {
        "success": False,
        "error": f"Unsupported activity type: {activity.sport_type}",
    }


def _handle_request(event: dict, invocation_id: str) -> dict:
    """
    Handle a single Strava webhook event

    :param event: The event dictionary containing event data
    :param invocation_id: The invocation ID for logging
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
            if user.is_active:
                return handle_activity_create(user, event, invocation_id)
            else:
                return {
                    "success": True,
                    "message": f"Activity {event.get('object_id')} created, but user is inactive",
                }
        if aspect_type in {"update", "delete"}:
            return {
                "success": True,
                "message": f"Activity {event.get('object_id')} {aspect_type}d",
            }

    return {"success": False, "error": f"Unknown event type: {event_type}"}


def handle_request(event: dict, invocation_id: str) -> dict:
    """
    Handle Strava webhook events sent from SQS

    :param event: Webhook event payload from SQS
    :param invocation_id: The invocation ID for logging
    :return: dict with {"success": bool, "responses": list of dicts
        with {"success": bool, "message": str (optional)}}
    """
    responses = []
    for record in event.get("Records"):
        try:
            responses.append(
                _handle_request(
                    event=json.loads(record.get("body")),
                    invocation_id=invocation_id,
                )
            )
        except Exception as e:
            responses.append({"success": False, "error": str(e)})
    return {"success": True, "responses": responses}
