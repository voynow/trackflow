import os

from dotenv import load_dotenv
from stravalib.client import Client

load_dotenv()
client = Client()

url = client.authorization_url(
    client_id=os.environ["STRAVA_CLIENT_ID"],
    redirect_uri="http://localhost:8000/notimplemented",
    scope=["read_all", "profile:read_all", "activity:read_all"],
)

# Go to this link, authorize the app, and retrieve the code from the URL
print(url)
