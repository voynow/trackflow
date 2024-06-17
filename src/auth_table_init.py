import os

from stravalib.client import Client

from src.supabase.client import upsert_user_auth
from src.supabase.models import UserAuthRow

strava_client = Client()


code = "..."
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
    id=athlete.id,
    access_token=strava_client.access_token,
    refresh_token=strava_client.refresh_token,
    expires_at=strava_client.token_expires_at,
)
upser_user_auth_response = upsert_user_auth(user_auth_row)
