import logging
import os
from datetime import datetime, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src import email_manager, supabase_client
from src.types.user import UserAuthRow, UserRow
from stravalib.client import Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
bearer_scheme = HTTPBearer()

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
        device_token=supabase_client.get_device_token(athlete_id),
    )
    supabase_client.upsert_user_auth(user_auth)
    return user_auth


def validate_and_refresh_token(token: str) -> int:
    """
    Validate and refresh the user's credentials in DB

    :param token: JWT token
    :return: athlete_id
    """
    try:
        athlete_id = decode_jwt(token)
    except jwt.ExpiredSignatureError:
        try:
            # If the token is expired, decode athlete_id and refresh
            athlete_id = decode_jwt(token, verify_exp=False)
            user_auth = supabase_client.get_user_auth(athlete_id)
            refresh_and_update_user_token(
                athlete_id=athlete_id, refresh_token=user_auth.refresh_token
            )
        except jwt.DecodeError:
            logger.error("Invalid JWT token")
            raise HTTPException(status_code=401, detail="Invalid JWT token")
        except Exception as e:
            logger.error(
                f"Unknown error validating and refreshing token: {e}",
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail="Internal server error")
    except jwt.DecodeError:
        logger.error("Invalid JWT token")
        raise HTTPException(status_code=401, detail="Invalid JWT token")
    except Exception as e:
        logger.error(
            f"Unknown error validating and refreshing token: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")

    return athlete_id


async def validate_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> UserRow:
    """
    Dependency that validates the JWT token from the Authorization header

    :param credentials: Bearer token credentials
    :return: UserRow
    """
    athlete_id = validate_and_refresh_token(credentials.credentials)
    if athlete_id is None:
        logger.error("Invalid authentication credentials")
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return supabase_client.get_user(athlete_id)


def authenticate_athlete(athlete_id: int) -> UserAuthRow:
    """
    Authenticate athlete with valid token, refresh if necessary

    :param athlete_id: strava internal identifier
    :return: UserAuthRow
    """
    user_auth = supabase_client.get_user_auth(athlete_id)
    if datetime.now(timezone.utc) < user_auth.expires_at:
        return user_auth
    return refresh_and_update_user_token(athlete_id, user_auth.refresh_token)


def get_configured_strava_client(user_auth: UserAuthRow) -> Client:
    strava_client.access_token = user_auth.access_token
    strava_client.refresh_token = user_auth.refresh_token
    strava_client.token_expires_at = user_auth.expires_at
    return strava_client


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
        device_token=supabase_client.get_device_token(athlete.id),
    )
    supabase_client.upsert_user_auth(user_auth_row)
    return user_auth_row


def signup(user_auth: UserAuthRow, email: Optional[str] = None) -> dict:
    """
    Sign up a new user

    :param user_auth: UserAuthRow
    :param email: User's email (optional)
    :return: Dictionary with success status and JWT token
    """
    email_manager.send_alert_email(
        subject="TrackFlow Alert: New Signup Attempt",
        text_content=f"You have a new client {email=} attempting to signup",
    )
    supabase_client.upsert_user(UserRow(athlete_id=user_auth.athlete_id))
    return {"success": True, "jwt_token": user_auth.jwt_token, "is_new_user": True}


def authenticate_on_signin(code: str, email: Optional[str] = None) -> dict:
    """
    Authenticate with Strava code, and sign up the user if they don't exist.

    :param code: Strava authorization code
    :param email: User's email (optional)
    :return: Dictionary with success status and JWT token
    """
    user_auth = authenticate_with_code(code)

    if not supabase_client.does_user_exist(user_auth.athlete_id):
        return signup(user_auth, email)

    return {
        "success": True,
        "jwt_token": user_auth.jwt_token,
        "is_new_user": False,
    }