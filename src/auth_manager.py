import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from stravalib.client import Client
from supabase_client import get_user_auth, upsert_user_auth
from supabase_models import UserAuthRow

load_dotenv()
strava_client = Client()


def get_configured_strava_client(user_auth: UserAuthRow) -> Client:
    strava_client.access_token = user_auth.access_token
    strava_client.refresh_token = user_auth.refresh_token
    strava_client.token_expires_at = user_auth.expires_at
    return strava_client


def refresh_and_update_user_token(athlete_id: int, refresh_token: str) -> UserAuthRow:
    print(
        f"{athlete_id=} token expired at {datetime.now(timezone.utc)}, refreshing token..."
    )
    access_info = strava_client.refresh_access_token(
        client_id=os.getenv("STRAVA_CLIENT_ID"),
        client_secret=os.getenv("STRAVA_CLIENT_SECRET"),
        refresh_token=refresh_token,
    )

    user_auth = UserAuthRow(
        athlete_id=athlete_id,
        access_token=access_info["access_token"],
        refresh_token=access_info["refresh_token"],
        expires_at=access_info["expires_at"],
    )
    upsert_user_auth(user_auth)
    return user_auth


def authenticate_athlete(athlete_id: int) -> UserAuthRow:
    user_auth = get_user_auth(athlete_id)
    if datetime.now(timezone.utc) < user_auth.expires_at:
        print(f"{athlete_id=} token still valid until {user_auth.expires_at}")
        return user_auth
    return refresh_and_update_user_token(athlete_id, user_auth.refresh_token)
