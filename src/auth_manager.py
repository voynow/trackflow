import logging
import os
from datetime import datetime, timezone
from typing import Optional

import jwt
from dotenv import load_dotenv
from stravalib.client import Client

from src.email_manager import send_alert_email
from src.supabase_client import (
    get_user_auth,
    upsert_user,
    upsert_user_auth,
    user_exists,
)
from src.types.user_auth_row import UserAuthRow
from src.types.user_row import UserRow

load_dotenv()
strava_client = Client()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def generate_jwt(athlete_id: int, expires_at: int) -> str:
    """
    Generate a JWT token using athlete_id and expiration time, aligning token
    expiration cycle with the athlete's Strava token

    :param athlete_id: strava internal identifier
    :param expires_at: expiration time of strava token
    :return: str
    """
    payload = {"athlete_id": athlete_id, "exp": expires_at}
    token = jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")
    return token


def decode_jwt(jwt_token: str, verify_exp: bool = True) -> int:
    """
    Decode JWT token and return athlete_id

    :param jwt_token: JWT token
    :param verify_exp: whether to verify expiration
    :return: int if successful, None if decoding fails
    :raises: jwt.DecodeError if token is invalid
    """
    payload = jwt.decode(
        jwt_token,
        os.environ["JWT_SECRET"],
        algorithms=["HS256"],
        options={"verify_exp": verify_exp},
    )
    return payload["athlete_id"]


def get_configured_strava_client(user_auth: UserAuthRow) -> Client:
    strava_client.access_token = user_auth.access_token
    strava_client.refresh_token = user_auth.refresh_token
    strava_client.token_expires_at = user_auth.expires_at
    return strava_client


def refresh_and_update_user_token(athlete_id: int, refresh_token: str) -> UserAuthRow:
    """
    Refresh the user's Strava token and update database

    :param athlete_id: strava internal identifier
    :param refresh_token: refresh token for Strava API
    :return: UserAuthRow
    """
    logger.info(f"Refreshing and updating token for athlete {athlete_id}")
    access_info = strava_client.refresh_access_token(
        client_id=os.environ["STRAVA_CLIENT_ID"],
        client_secret=os.environ["STRAVA_CLIENT_SECRET"],
        refresh_token=refresh_token,
    )
    new_jwt_token = generate_jwt(
        athlete_id=athlete_id, expires_at=access_info["expires_at"]
    )
    user_auth = UserAuthRow(
        athlete_id=athlete_id,
        access_token=access_info["access_token"],
        refresh_token=access_info["refresh_token"],
        expires_at=access_info["expires_at"],
        jwt_token=new_jwt_token,
    )
    upsert_user_auth(user_auth)
    return user_auth


def authenticate_athlete(athlete_id: int) -> UserAuthRow:
    """
    Authenticate athlete with valid token, refresh if necessary

    :param athlete_id: strava internal identifier
    :return: UserAuthRow
    """
    user_auth = get_user_auth(athlete_id)
    if datetime.now(timezone.utc) < user_auth.expires_at:
        return user_auth
    return refresh_and_update_user_token(athlete_id, user_auth.refresh_token)


def get_strava_client(athlete_id: int) -> Client:
    """Interface for retrieving a Strava client with valid authentication"""
    user_auth = authenticate_athlete(athlete_id)
    return get_configured_strava_client(user_auth)


def authenticate_with_code(code: str) -> UserAuthRow:
    """
    Authenticate athlete with code, exchange with strava client for token,
    generate new JWT, and update database

    :param code: temporary authorization code
    :return: UserAuthRow
    """
    token = strava_client.exchange_code_for_token(
        client_id=os.environ["STRAVA_CLIENT_ID"],
        client_secret=os.environ["STRAVA_CLIENT_SECRET"],
        code=code,
    )
    strava_client.access_token = token["access_token"]
    strava_client.refresh_token = token["refresh_token"]
    strava_client.token_expires_at = token["expires_at"]

    athlete = strava_client.get_athlete()

    jwt_token = generate_jwt(athlete_id=athlete.id, expires_at=token["expires_at"])

    user_auth_row = UserAuthRow(
        athlete_id=athlete.id,
        access_token=strava_client.access_token,
        refresh_token=strava_client.refresh_token,
        expires_at=strava_client.token_expires_at,
        jwt_token=jwt_token,
    )
    upsert_user_auth(user_auth_row)
    return user_auth_row


def signup(code: str, email: Optional[str] = None) -> dict:
    """
    Get authenticated user, upsert user with email and preferences

    :param email: user email
    :param code: strava code
    :return: jwt_token
    """
    preferences = (
        "I'm looking to improve my running performance while being smart and realistic."
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


def signup_with_user_auth(user_auth: UserAuthRow) -> dict:
    """ """
    preferences = (
        "I'm looking to improve my running performance while being smart and realistic."
    )
    upsert_user(UserRow(athlete_id=user_auth.athlete_id, preferences=preferences))
    return {"success": True, "jwt_token": user_auth.jwt_token}


def authenticate_and_maybe_signup(code: str, email: Optional[str] = None) -> dict:
    """
    Authenticate with Strava code, and sign up the user if they don't exist.

    :param code: Strava authorization code
    :param email: User's email (optional)
    :return: Dictionary with success status and JWT token
    """
    user_auth = authenticate_with_code(code)

    if not user_exists(user_auth.athlete_id):
        return signup_with_user_auth(user_auth)

    return {"success": True, "jwt_token": user_auth.jwt_token}
