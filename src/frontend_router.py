from typing import Callable, Dict, Optional

import jwt

from src import auth_manager
from src.supabase_client import (
    get_training_week,
    get_user,
    update_preferences,
)


def get_training_week_handler(athlete_id: str, payload: Optional[dict] = None) -> dict:
    """Handle get_training_week request."""
    training_week = get_training_week(athlete_id)
    return {
        "success": True,
        "training_week": training_week.json(),
    }


def get_profile_handler(athlete_id: str, payload: Optional[dict] = None) -> dict:
    """Handle get_profile request."""
    user = get_user(athlete_id)
    athlete = auth_manager.get_strava_client(athlete_id).get_athlete()
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


def update_preferences_handler(athlete_id: str, payload: Optional[dict] = None) -> dict:
    """Handle update_preferences request."""
    if payload is None or "preferences" not in payload:
        return {"success": False, "error": "Missing preferences in payload"}
    update_preferences(athlete_id=athlete_id, preferences_json=payload["preferences"])
    return {"success": True}


METHOD_HANDLERS: Dict[str, Callable[[str, Optional[dict]], dict]] = {
    "get_training_week": get_training_week_handler,
    "get_profile": get_profile_handler,
    "update_preferences": update_preferences_handler,
}


def handle_request(jwt_token: str, method: str, payload: Optional[dict] = None) -> dict:
    """
    Handle various requests based on the provided method.

    :param jwt_token: JWT token for authentication
    :param method: The method to be executed
    :param payload: Optional dictionary with additional data
    :return: Dictionary with the result of the operation
    """
    try:
        athlete_id = auth_manager.decode_jwt(jwt_token)
    except jwt.DecodeError:
        return {"success": False, "error": "Invalid JWT token"}

    if method in METHOD_HANDLERS:
        return METHOD_HANDLERS[method](athlete_id, payload)
    else:
        return {"success": False, "error": f"Invalid method: {method}"}