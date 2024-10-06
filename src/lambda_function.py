import logging
import os
from typing import Optional

import jwt

from src.auth_manager import authenticate_with_code, decode_jwt, get_strava_client
from src.daily_pipeline import daily_executor, webhook_executor
from src.email_manager import send_alert_email
from src.supabase_client import (
    get_training_week,
    get_user,
    list_users,
    update_preferences,
    upsert_user,
)
from src.types.user_row import UserRow

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def signup(email: str, code: str) -> dict:
    """
    Get authenticated user, upsert user with email and preferences

    :param email: user email
    :param code: strava code
    :return: jwt_token
    """
    preferences = (
        "Looking for smart training recommendations to optimize my performance."
    )
    send_alert_email(
        subject="TrackFlow Alert: New Signup Attempt",
        text_content=f"You have a new client {email=} attempting to signup with {preferences=}",
    )
    user_auth = authenticate_with_code(code)
    upsert_user(
        UserRow(
            athlete_id=user_auth.athlete_id,
            email=email,
            preferences=preferences,
        )
    )
    return {"success": True, "jwt_token": user_auth.jwt_token}


def handle_frontend_request(
    jwt_token: str, method: str, payload: Optional[dict] = None
) -> dict:
    """
    To be extended for other requests eventually

    Validate JWT, then return training week with coaching

    :param jwt_token: jwt_token
    :param method: method
    :param payload: optional dictionary with additional data
    :return: dict with {"success": bool}
    """
    try:
        athlete_id = decode_jwt(jwt_token)
    except jwt.DecodeError:
        return {"success": False, "error": "Invalid JWT token"}

    if method == "get_training_week":
        training_week = get_training_week(athlete_id)
        return {
            "success": True,
            "training_week": training_week.json(),
        }
    elif method == "get_profile":
        user = get_user(athlete_id)
        athlete = get_strava_client(athlete_id).get_athlete()
        return {
            "success": True,
            "profile": {
                "firstname": athlete.firstname,
                "lastname": athlete.lastname,
                "profile": athlete.profile,
                "email": user.email,
                "preferences": user.preferences_json.json(),
                "is_active": user.is_active,
            },
        }
    elif method == "update_preferences":
        update_preferences(
            athlete_id=athlete_id, preferences_json=payload["preferences"]
        )
        return {"success": True}
    else:
        return {"success": False, "error": f"Invalid method: {method}"}


def handle_strava_webhook(event: dict) -> dict:
    """
    Handle Strava webhook events for activities and athletes.

    :param event: Webhook event payload from Strava
    :return: dict with {"success": bool}
    """
    subscription_id = int(event.get("subscription_id"))
    expected_subscription_id = int(os.environ["STRAVA_WEBHOOK_SUBSCRIPTION_ID"])
    if subscription_id != expected_subscription_id:
        return {
            "success": False,
            "error": f"Invalid subscription ID: {event.get('subscription_id')}",
        }

    if event.get("object_type") == "activity":
        if event.get("aspect_type") == "create":
            return webhook_executor(get_user(event.get("owner_id")))
        elif event.get("aspect_type") == "update":
            return {
                "success": True,
                "message": f"Activity {event.get('object_id')} updated",
            }
        elif event.get("aspect_type") == "delete":
            return {
                "success": True,
                "message": f"Activity {event.get('object_id')} deleted",
            }
    return {"success": False, "error": f"Unknown event type: {event}"}


def daily_exe_orchestrator() -> dict:
    for user in list_users():
        if user.is_active:
            daily_executor(user)
    return {"success": True}


def strategy_router(event: dict) -> dict:

    # Will fail on bad authenticate_with_code
    if event.get("email") and event.get("code"):
        return signup(
            email=event["email"],
            code=event["code"],
        )

    # Will fail on bad authenticate_with_code
    elif event.get("code"):
        user_auth = authenticate_with_code(event["code"])
        return {"success": True, "jwt_token": user_auth.jwt_token}

    elif event.get("jwt_token") and event.get("method"):
        return handle_frontend_request(
            jwt_token=event["jwt_token"],
            method=event["method"],
            payload=event.get("payload"),
        )

    elif (
        event.get("subscription_id")
        and event.get("aspect_type")
        and event.get("object_type")
        and event.get("object_id")
        and event.get("owner_id")
    ):
        return handle_strava_webhook(event)

    # This will only run if triggered by NIGHTLY_EMAIL_TRIGGER_ARN
    elif (
        event.get("resources")
        and event.get("resources")[0] == os.environ["NIGHTLY_EMAIL_TRIGGER_ARN"]
    ):
        return daily_exe_orchestrator()

    elif event.get("trigger_test_key") == os.environ["TRIGGER_TEST_KEY"]:
        daily_executor(get_user(os.environ["JAMIES_ATHLETE_ID"]))
        return {"success": True}
    else:
        return {"success": False, "error": f"Unknown event type: {event}"}


def lambda_handler(event, context):
    """
    Main entry point, responsible for logging and error handling, producing
    email alerts on errors and failures

    :param event: lambda event
    :param context: lambda context
    :return: dict with {"success": bool}
    """
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    try:
        response = strategy_router(event)
    except Exception as e:
        response = {"success": False, "error": str(e)}

    # Ensure response is a dictionary
    if type(response) is not dict:
        response = {"success": False, "error": f"Unknown response type: {response}"}

    # Ensure response has success key
    if "success" not in response:
        response = {"success": False, "error": f"Unknown response: {response}"}

    # Send alert on any and all errors/failures
    if response["success"]:
        return response
    else:
        send_alert_email(
            subject="TrackFlow Alert: Error in lambda_handler",
            text_content=response["error"],
        )
        return {"success": False}
