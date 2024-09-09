import logging
import os
import traceback
from typing import Optional

import jwt

from src.activities import (
    get_activities_df,
    get_activity_summaries,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.auth_manager import authenticate_with_code, decode_jwt
from src.constants import COACH_ROLE
from src.email_manager import send_alert_email
from src.auth_manager import authenticate_with_code
from src.daily_pipeline import (
    daily_generic_pipeline,
    mid_week_update_pipeline,
    new_training_week_pipeline,
)
from src.email_manager import send_alert_email
from src.supabase_client import (
    get_training_week,
    list_users,
    upsert_user,
)
from src.types.training_week import TrainingWeek
from src.types.user_row import UserRow
from src.utils import datetime_now_est


def signup(email: str, preferences: str, code: str) -> str:
    """
    Get authenticated user, upsert user with email and preferences

    :param email: user email
    :param preferences: user preferences
    :param code: strava code
    :return: jwt_token
    """
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


def handle_frontend_request(jwt_token: str):
    """
    To be extended for other requests eventually

    Validate JWT, then return training week with coaching
    """
    try:
        athlete_id = decode_jwt(jwt_token)
        training_week = get_training_week(athlete_id)
        return {
            "success": True,
            "training_week": training_week.json(),
        }
    except jwt.DecodeError:
        return {"success": False, "error": "Invalid JWT token"}


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
                email_subject="Training Schedule Update 🏃‍♂️🎯",
            )
    except Exception as e:
        logging.error(f"Error processing user {user.athlete_id}: {e}")
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
    print(f"Event: {event}")
    print(f"Context: {context}")

    # Will fail on bad authenticate_with_code
    if event.get("email") and event.get("preferences") and event.get("code"):
        response = signup(
            email=event["email"],
            preferences=event["preferences"],
            code=event["code"],
        )
        return {"success": True, "jwt_token": response}

    # Will fail on bad authenticate_with_code
    elif event.get("code"):
        user_auth = authenticate_with_code(event["code"])
        return {"success": True, "jwt_token": user_auth.jwt_token}

    elif event.get("jwt_token"):
        return handle_frontend_request(event["jwt_token"])

    # This will only run if triggered by NIGHTLY_EMAIL_TRIGGER_ARN
    elif (
        event.get("resources")
        and event.get("resources")[0] == os.environ["NIGHTLY_EMAIL_TRIGGER_ARN"]
    ):
        [daily_executor(user) for user in list_users()]
        return {"success": True}

    # Catch any error routing or funny business
    else:
        send_alert_email(
            subject="TrackFlow Alert: Unknown Lambda Invocation",
            text_content=f"Unknown invocation of lambda with {event=} and {context=}",
        )
        return {"success": False}
