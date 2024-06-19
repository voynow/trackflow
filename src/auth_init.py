import os

from dotenv import load_dotenv
from stravalib.client import Client
from supabase_client import upsert_user_auth
from supabase_models import UserAuthRow

load_dotenv()
strava_client = Client()


def get_strava_oauth_url() -> None:
    url = strava_client.authorization_url(
        client_id=os.environ["STRAVA_CLIENT_ID"],
        redirect_uri="http://localhost:8000/notimplemented",
        scope=["read_all", "profile:read_all", "activity:read_all"],
    )

    # Go to this link, authorize the app, and retrieve the code from the URL
    print(url)


def authenticate_with_code(code) -> None:
    token = strava_client.exchange_code_for_token(
        client_id=os.environ["STRAVA_CLIENT_ID"],
        client_secret=os.environ["STRAVA_CLIENT_SECRET"],
        code=code,
    )
    strava_client.access_token = token["access_token"]
    strava_client.refresh_token = token["refresh_token"]
    strava_client.token_expires_at = token["expires_at"]

    athlete = strava_client.get_athlete()

    user_auth_row = UserAuthRow(
        athlete_id=athlete.id,
        access_token=strava_client.access_token,
        refresh_token=strava_client.refresh_token,
        expires_at=strava_client.token_expires_at,
    )
    upsert_user_auth(user_auth_row)
