import logging
import os
import sys
import traceback
from typing import Optional

import jwt

from src.auth_manager import authenticate_with_code, decode_jwt, get_strava_client
from src.daily_pipeline import (
    daily_generic_pipeline,
    mid_week_update_pipeline,
    new_training_week_pipeline,
)
from src.email_manager import send_alert_email
from src.supabase_client import (
    get_training_week,
    get_user,
    list_users,
    update_preferences,
    upsert_user,
)
from src.types.training_week import TrainingWeek
from src.types.user_row import UserRow
from src.utils import datetime_now_est

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def signup(email: str, code: str) -> str:
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
    return user_auth.jwt_token


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

    try:
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
            return {"success": False, "error": "Invalid method"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def daily_executor(user: UserRow) -> Optional[TrainingWeek]:
    """Decides between generating a new week or updating based on the day."""
    try:
        # Sunday is day 6
        if datetime_now_est().weekday() == 6:
            return daily_generic_pipeline(
                user=user,
                pipeline_function=new_training_week_pipeline,
                email_subject="Training Schedule Just Dropped 🏃‍♂️🎯",
            )
        else:
            return daily_generic_pipeline(
                user=user,
                pipeline_function=mid_week_update_pipeline,
                email_subject="www.trackflow.xyz is live! 🏃‍♂️🎯",
            )
    except Exception as e:
        logger.error(f"Error processing user {user.athlete_id}: {e}")
        send_alert_email(
            subject="TrackFlow Alert: Error in Lambda Function",
            text_content=f"Error for {user.email=} {e} with traceback: {traceback.format_exc()}",
        )
        return None


def lambda_handler(event, context):
    """
    Main entry point for production workload. For simplicity, I've designed this
    lambda to act like an API of sorts, using if/else logic to route events to
    the correct function.

    :param event: lambda event
    :param context: lambda context
    :return: dict with {"success": bool}
    """
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    # Will fail on bad authenticate_with_code
    if event.get("email") and event.get("code"):
        response = signup(
            email=event["email"],
            code=event["code"],
        )
        return {"success": True, "jwt_token": response}

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

    # This will only run if triggered by NIGHTLY_EMAIL_TRIGGER_ARN
    elif (
        event.get("resources")
        and event.get("resources")[0] == os.environ["NIGHTLY_EMAIL_TRIGGER_ARN"]
    ):
        for user in list_users():
            if user.is_active:
                daily_executor(user)
        return {"success": True}

    elif event.get("trigger_test_key") == os.environ["TRIGGER_TEST_KEY"]:
        daily_executor(get_user(os.environ["JAMIES_ATHLETE_ID"]))
        return {"success": True}

    # Catch any error routing or funny business
    else:
        send_alert_email(
            subject="TrackFlow Alert: Unknown Lambda Invocation",
            text_content=f"Unknown invocation of lambda with {event=} and {context=}",
        )
        return {"success": False}
