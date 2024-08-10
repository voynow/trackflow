import datetime
import os

from dotenv import load_dotenv
from postgrest.base_request_builder import APIResponse
from supabase import Client, create_client

from src.types.training_week_with_coaching import TrainingWeekWithCoaching
from src.types.user_auth_row import UserAuthRow

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


def upsert_training_week_with_coaching(
    athlete_id: int,
    training_week_with_coaching: TrainingWeekWithCoaching,
) -> APIResponse:
    """
    Upsert a row into the training_week_with_coaching table.

    :param athlete_id: The ID of the athlete.
    :param training_week_with_coaching: An instance of TrainingWeekWithCoaching.
    :return: APIResponse from Supabase.
    """
    row_data = {
        "athlete_id": athlete_id,
        "training_week": training_week_with_coaching.training_week.json(),
        "typical_week_training_review": training_week_with_coaching.typical_week_training_review,
        "weekly_mileage_target": training_week_with_coaching.weekly_mileage_target,
    }

    table = client.table("training_week_with_coaching")
    response = table.upsert(row_data).execute()

    return response
