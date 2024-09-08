import datetime
import json
import os

from dotenv import load_dotenv
from postgrest.base_request_builder import APIResponse
from supabase import Client, create_client

from src.types.training_week import TrainingWeek
from src.types.user_auth_row import UserAuthRow
from src.types.user_row import UserRow

load_dotenv()


def init() -> Client:
    """ """
    url: str = os.environ["SUPABASE_URL"]
    key: str = os.environ["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase


client = init()


def upsert_user_auth(user_auth_row: UserAuthRow) -> APIResponse:
    """
    Convert UserAuthRow to a dictionary, ensure json serializable expires_at,
    and upsert into user_auth table handling duplicates on athlete_id

    :param user_auth_row: A dictionary representation of UserAuthRow
    :return: APIResponse
    """
    user_auth_row = user_auth_row.dict()
    if isinstance(user_auth_row["expires_at"], datetime.datetime):
        user_auth_row["expires_at"] = user_auth_row["expires_at"].isoformat()

    table = client.table("user_auth")
    response = table.upsert(user_auth_row, on_conflict="athlete_id").execute()

    return response


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


def list_athlete_ids() -> list[int]:
    """
    List all athlete_ids in the user_auth table

    :return: list of athlete_ids
    """
    table = client.table("user_auth")
    response = table.select("athlete_id").execute()

    return [row["athlete_id"] for row in response.data]


def upsert_user(user_row: UserRow) -> APIResponse:
    """
    Upsert a row into the user table

    :param user_row: An instance of UserRow
    :return: APIResponse from Supabase
    """
    row_data = user_row.dict()
    if isinstance(row_data["created_at"], datetime.datetime):
        row_data["created_at"] = row_data["created_at"].isoformat()

    table = client.table("user")
    response = table.upsert(row_data, on_conflict="athlete_id").execute()

    return response


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


def get_training_week(athlete_id: int) -> TrainingWeek:
    """
    Get the most recent training_week row by athlete_id

    :param athlete_id: The ID of the athlete
    :return: An instance of TrainingWeek
    """
    table = client.table("training_week")
    response = (
        table.select("training_week")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    try:
        response_data = response.data[0]
    except Exception:
        raise ValueError(
            f"Could not find training_week row with {athlete_id=}",
            exc_info=True,
        )

    return TrainingWeek(**json.loads(response_data["training_week"]))


def upsert_training_week(
    athlete_id: int,
    training_week: TrainingWeek,
) -> APIResponse:
    """Upsert a row into the training_week table"""

    row_data = {
        "athlete_id": athlete_id,
        "training_week": training_week.json(),
    }

    table = client.table("training_week")
    response = table.upsert(row_data).execute()

    return response
