import os
from datetime import datetime, timezone

import jwt
from dotenv import load_dotenv
from stravalib.client import Client

from src.supabase_client import get_user_auth, upsert_user_auth
from src.types.user_auth_row import UserAuthRow

load_dotenv()
strava_client = Client()


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
