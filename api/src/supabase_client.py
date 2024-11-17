from __future__ import annotations

import datetime
import json
import os
from typing import Optional

from dotenv import load_dotenv
from src.types.mileage_recommendation import (
    MileageRecommendation,
    MileageRecommendationRow,
)
from src.types.training_week import TrainingWeek
from src.types.user import Preferences, UserAuthRow, UserRow
from supabase import Client, create_client

load_dotenv()


def init() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)


client = init()


def get_device_token(athlete_id: int) -> Optional[str]:
    """
    Get the device token for a user in the database.

    :param athlete_id: The athlete's ID
    :return: The device token for the user, or None if the user does not exist
    """
    try:
        user_auth = get_user_auth(athlete_id)
        return user_auth.device_token
    except ValueError:
        return None


def get_user(athlete_id: int) -> UserRow:
    """
    Get a user by athlete_id

    :param athlete_id: int
    :return: UserRow
    """
    table = client.table("user")
    response = table.select("*").eq("athlete_id", athlete_id).execute()

    if not response.data:
        raise ValueError(f"Could not find user with {athlete_id=}")

    return UserRow(**response.data[0])


def list_users() -> list[UserRow]:
    """
    List all users in the user_auth table

    :return: list of UserAuthRow
    """
    table = client.table("user")
    response = table.select("*").execute()

    return [UserRow(**row) for row in response.data]


def get_user_auth(athlete_id: int) -> UserAuthRow:
    """
    Get user_auth row by athlete_id

    :param athlete_id: int
    :return: APIResponse
    """
    table = client.table("user_auth")
    response = table.select("*").eq("athlete_id", athlete_id).execute()

    if not response.data:
        raise ValueError(f"Cound not find user_auth row with {athlete_id=}")

    return UserAuthRow(**response.data[0])


def get_training_week(athlete_id: int) -> TrainingWeek:
    """
    Get the most recent training_week row by athlete_id.

    :param athlete_id: int
    :return: TrainingWeek
    """
    table = client.table("training_week")
    response = (
        table.select("training_week")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise ValueError(
            f"Could not find training_week row for athlete_id {athlete_id}"
        )

    try:
        json_data = json.loads(response.data[0]["training_week"])

        # temp requirement to remove legacy moderate run
        sessions = []
        for session in json_data["sessions"]:
            if session["session_type"] == "moderate run":
                session["session_type"] = "easy run"
            sessions.append(session)

        return TrainingWeek(sessions=sessions)
    except IndexError:
        raise ValueError(
            f"Could not find training_week row for athlete_id {athlete_id}"
        )


def upsert_user_auth(user_auth_row: UserAuthRow) -> None:
    """
    Convert UserAuthRow to a dictionary, ensure json serializable expires_at,
    and upsert into user_auth table handling duplicates on athlete_id

    :param user_auth_row: A dictionary representation of UserAuthRow
    """
    user_auth_row = user_auth_row.dict()
    if isinstance(user_auth_row["expires_at"], datetime.datetime):
        user_auth_row["expires_at"] = user_auth_row["expires_at"].isoformat()

    table = client.table("user_auth")
    table.upsert(user_auth_row, on_conflict="athlete_id").execute()


def update_user_device_token(athlete_id: str, device_token: str) -> None:
    """
    Update the device token for a user in the database.

    :param athlete_id: The athlete's ID
    :param device_token: The device token for push notifications
    """
    client.table("user_auth").update({"device_token": device_token}).eq(
        "athlete_id", athlete_id
    ).execute()


def update_preferences(athlete_id: int, preferences: dict):
    """
    Update user's preferences

    :param athlete_id: The ID of the athlete
    :param preferences: A Preferences object as a dictionary
    """
    try:
        Preferences(**preferences)
    except Exception as e:
        raise ValueError("Invalid preferences") from e

    table = client.table("user")
    table.update({"preferences": preferences}).eq("athlete_id", athlete_id).execute()


def upsert_user(user_row: UserRow):
    """
    Upsert a row into the user table

    :param user_row: An instance of UserRow
    """
    row_data = user_row.dict()
    if isinstance(row_data["created_at"], datetime.datetime):
        row_data["created_at"] = row_data["created_at"].isoformat()

    table = client.table("user")
    table.upsert(row_data, on_conflict="athlete_id").execute()


def does_user_exist(athlete_id: int) -> bool:
    """
    Check if a user exists in the user table

    :param athlete_id: The ID of the athlete
    :return: True if the user exists, False otherwise
    """
    table = client.table("user")
    response = table.select("*").eq("athlete_id", athlete_id).execute()
    return bool(response.data)


def upsert_training_week(
    athlete_id: int,
    training_week: TrainingWeek,
):
    """Upsert a row into the training_week table"""
    row_data = {
        "athlete_id": athlete_id,
        "training_week": training_week.json(),
    }
    table = client.table("training_week")
    table.upsert(row_data).execute()


def has_user_updated_today(athlete_id: int) -> bool:
    """
    Check if the user has received an update today. Where "today" is defined as
    within the past 23 hours and 30 minutes (to account for any delays in
    yesterday's evening update).

    :param athlete_id: The ID of the athlete
    :return: True if the user has received an update today, False otherwise
    """
    table = client.table("training_week")
    response = (
        table.select("*")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        return False

    # "Has this user posted an activity in the last 23 hours and 30 minutes?"
    time_diff = datetime.datetime.now(
        datetime.timezone.utc
    ) - datetime.datetime.fromisoformat(response.data[0]["created_at"])
    return time_diff < datetime.timedelta(hours=23, minutes=30)


def insert_mileage_recommendation(
    athlete_id: int,
    mileage_recommendation: MileageRecommendation,
    year: int,
    week_of_year: int,
):
    """
    Insert a row into the mileage_recommendations table

    :param mileage_recommendation: A MileageRecommendation object
    """
    row_data = {
        "athlete_id": athlete_id,
        "year": year,
        "week_of_year": week_of_year,
        **mileage_recommendation.dict(),
    }
    print(row_data)
    table = client.table("mileage_recommendation")
    table.upsert(row_data).execute()


def get_mileage_recommendation(
    athlete_id: int, year: int, week_of_year: int
) -> MileageRecommendation:
    """
    Get the most recent mileage recommendation for the given year and week of year

    :param athlete_id: The ID of the athlete
    :param year: The year of the recommendation
    :param week_of_year: The week of the year of the recommendation
    :return: A MileageRecommendation object
    """
    table = client.table("mileage_recommendation")
    response = (
        table.select("*")
        .eq("athlete_id", athlete_id)
        .eq("year", year)
        .eq("week_of_year", week_of_year)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise ValueError(
            f"Could not find mileage recommendation for {athlete_id=} {year=} {week_of_year=}"
        )
    data = MileageRecommendationRow(**response.data[0])
    return MileageRecommendation(
        thoughts=data.thoughts, total_volume=data.total_volume, long_run=data.long_run
    )
