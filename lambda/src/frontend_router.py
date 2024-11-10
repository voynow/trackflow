from typing import Callable, Dict, Optional

import jwt

from src import auth_manager
from src.supabase_client import (
    get_user,
    get_user_auth,
)
from src.types.update_pipeline import ExeType
from src.update_pipeline import update_training_week


def start_onboarding(athlete_id: str, payload: dict) -> dict:
    """Handle start_onboarding request."""
    user = get_user(athlete_id)
    update_training_week(user, ExeType.NEW_WEEK)
    update_training_week(user, ExeType.MID_WEEK)
    return {"success": True}


METHOD_HANDLERS: Dict[str, Callable[[str, Optional[dict]], dict]] = {
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
