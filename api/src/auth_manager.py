import logging
import os
from typing import Optional

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src import supabase_client
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
