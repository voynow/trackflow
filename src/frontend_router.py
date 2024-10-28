import time
from typing import Callable, Dict, Optional

import jwt

from src import auth_manager
from src.activities import get_activities_df, get_weekly_summaries
from src.auth_manager import get_strava_client
from src.supabase_client import (
    get_training_week,
    get_user,
    get_user_auth,
    update_preferences,
)
from src.types.update_pipeline import ExeType
from src.update_pipeline import training_week_update_executor


def get_training_week_handler(athlete_id: str, payload: dict) -> dict:
    """Handle get_training_week request."""
    start = time.time()
    training_week = get_training_week(athlete_id)
    end = time.time()
    print(f"get_training_week took {end - start} seconds")
    return {
        "success": True,
        "training_week": training_week.json(),
    }


def get_profile_handler(athlete_id: str, payload: dict) -> dict:
    """Handle get_profile request."""
    start = time.time()
    user = get_user(athlete_id)
    athlete = auth_manager.get_strava_client(athlete_id).get_athlete()
    end = time.time()
    print(f"get_profile took {end - start} seconds")
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


def update_preferences_handler(athlete_id: str, payload: dict) -> dict:
    """Handle update_preferences request."""
    if payload is None or "preferences" not in payload:
        return {"success": False, "error": "Missing preferences in payload"}
    update_preferences(athlete_id=athlete_id, preferences_json=payload["preferences"])
    return {"success": True}


def get_weekly_summaries_handler(athlete_id: str, payload: dict) -> dict:
    """
    Handle get_weekly_summaries request

    :param athlete_id: The athlete ID
    :param payload: unused payload
    :return: List of WeekSummary objects as JSON
    """
    start = time.time()
    user = get_user(athlete_id)
    strava_client = get_strava_client(user.athlete_id)
    activities_df = get_activities_df(strava_client)
    weekly_summaries = get_weekly_summaries(activities_df)
    end = time.time()
    print(f"get_weekly_summaries took {end - start} seconds")
    return {
        "success": True,
        "weekly_summaries": [summary.json() for summary in weekly_summaries],
    }


def start_onboarding(athlete_id: str, payload: dict) -> dict:
    """Handle start_onboarding request."""
    user = get_user(athlete_id)
    training_week_update_executor(user, ExeType.NEW_WEEK, "onboarding-trigger")
    training_week_update_executor(user, ExeType.MID_WEEK, "onboarding-trigger")
    return {"success": True}


METHOD_HANDLERS: Dict[str, Callable[[str, Optional[dict]], dict]] = {
    "get_training_week": get_training_week_handler,
    "get_profile": get_profile_handler,
    "update_preferences": update_preferences_handler,
    "get_weekly_summaries": get_weekly_summaries_handler,
    "start_onboarding": start_onboarding,
}


def handle_request(jwt_token: str, method: str, payload: Optional[dict] = {}) -> dict:
    """
    Handle various requests based on the provided method.

    :param jwt_token: JWT token for authentication
    :param method: The method to be executed
    :param payload: Optional dictionary with additional data
    :return: Dictionary with the result of the operation
    """
    try:
        athlete_id = auth_manager.decode_jwt(jwt_token)
    except jwt.ExpiredSignatureError:
        try:
            # If the token is expired, decode athlete_id and refresh
            athlete_id = auth_manager.decode_jwt(jwt_token, verify_exp=False)
            user_auth = get_user_auth(athlete_id)
            auth_manager.refresh_and_update_user_token(
                athlete_id=athlete_id, refresh_token=user_auth.refresh_token
            )
        except jwt.DecodeError:
            return {"success": False, "error": "Invalid JWT token"}
    except jwt.DecodeError:
        return {"success": False, "error": "Invalid JWT token"}

    if method in METHOD_HANDLERS:
        return METHOD_HANDLERS[method](athlete_id, payload)
    else:
        return {"success": False, "error": f"Invalid method: {method}"}
