import os

from fastapi.testclient import TestClient
from src import supabase_client
from src.main import app
from src.types.training_week import TrainingWeek

client = TestClient(app)


def test_get_training_week():
    """Test successful retrieval of training week"""
    user_auth = supabase_client.get_user_auth(os.environ["JAMIES_ATHLETE_ID"])

    response = client.get(
        "/training_week/", headers={"Authorization": f"Bearer {user_auth.jwt_token}"}
    )
    assert TrainingWeek(**response.json())
    assert response.status_code == 200


def test_update_device_token():
    """Test successful update of device token"""
    user_auth = supabase_client.get_user_auth(os.environ["JAMIES_ATHLETE_ID"])
    response = client.post(
        "/device_token/",
        json={"device_token": user_auth.device_token},
        headers={"Authorization": f"Bearer {user_auth.jwt_token}"},
    )
    assert response.status_code == 200


def test_update_preferences():
    """Test successful update of preferences"""
    user_auth = supabase_client.get_user_auth(os.environ["JAMIES_ATHLETE_ID"])
    user = supabase_client.get_user(os.environ["JAMIES_ATHLETE_ID"])
    response = client.post(
        "/preferences/",
        json={"preferences": user.preferences.dict()},
        headers={"Authorization": f"Bearer {user_auth.jwt_token}"},
    )
    assert response.status_code == 200


def test_get_profile():
    """Test successful retrieval of profile"""
    user_auth = supabase_client.get_user_auth(os.environ["JAMIES_ATHLETE_ID"])
    response = client.get(
        "/profile/", headers={"Authorization": f"Bearer {user_auth.jwt_token}"}
    )
    assert response.status_code == 200


def test_get_weekly_summaries():
    """Test successful retrieval of weekly summaries"""
    user_auth = supabase_client.get_user_auth(os.environ["JAMIES_ATHLETE_ID"])
    response = client.get(
        "/weekly_summaries/", headers={"Authorization": f"Bearer {user_auth.jwt_token}"}
    )
    assert response.status_code == 200


def test_authenticate():
    """Test successful authentication, only covering does_user_exist"""
    user = supabase_client.get_user(os.environ["JAMIES_ATHLETE_ID"])
    assert supabase_client.does_user_exist(user.athlete_id)


def test_strava_webhook():
    """Test successful Strava webhook"""
    event = {
        "subscription_id": 288883,
        "aspect_type": "update",
        "object_type": "activity",
        "object_id": 18888888889,
        "owner_id": 98888886,
        "event_time": 1731515699,
        "updates": {"title": "Best running weather ❄️"},
    }
    response = client.post("/strava-webhook/", json=event)
    assert response.status_code == 200
