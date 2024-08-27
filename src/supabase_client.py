import datetime
import json
import os

from dotenv import load_dotenv
from postgrest.base_request_builder import APIResponse
from supabase import Client, create_client

from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import TrainingWeekWithCoaching, TrainingWeekWithPlanning
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


def list_users() -> list[UserRow]:
    """
    List all users in the user_auth table

    :return: list of UserAuthRow
    """
    table = client.table("user")
    response = table.select("*").execute()

    return [UserRow(**row) for row in response.data]


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
        "training_week_planning": training_week_with_coaching.training_week_planning,
        "training_week": json.dumps(
            [session.dict() for session in training_week_with_coaching.training_week]
        ),
        "typical_week_training_review": training_week_with_coaching.typical_week_training_review,
        "weekly_mileage_target": training_week_with_coaching.weekly_mileage_target,
    }

    table = client.table("training_week_with_coaching")
    response = table.upsert(row_data).execute()

    return response


def mock_upsert_training_week_with_coaching(
    athlete_id: int,
    training_week_with_coaching: TrainingWeekWithCoaching,
) -> APIResponse:
    """
    Mock version of upsert_training_week_with_coaching for testing.

    :param athlete_id: The ID of the athlete.
    :param training_week_with_coaching: An instance of TrainingWeekWithCoaching.
    :return: Mocked APIResponse object.
    """
    row_data = {
        "athlete_id": athlete_id,
        "training_week_planning": training_week_with_coaching.training_week_planning,
        "training_week": [
            session.dict() for session in training_week_with_coaching.training_week
        ],
        "typical_week_training_review": training_week_with_coaching.typical_week_training_review,
        "weekly_mileage_target": training_week_with_coaching.weekly_mileage_target,
    }

    print(json.dumps(row_data, indent=4))
    print(f"{training_week_with_coaching.total_weekly_mileage=}")
    return APIResponse(data=[row_data], count=1)


def get_training_week_with_coaching(athlete_id: int) -> TrainingWeekWithCoaching:
    """
    Get the most recent training_week_with_coaching row by athlete_id

    :param athlete_id: The ID of the athlete
    :return: An instance of TrainingWeekWithCoaching
    """
    table = client.table("training_week_with_coaching")
    response = (
        table.select("*")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    try:
        response_data = response.data[0]
    except Exception:
        raise ValueError(
            f"Could not find training_week_with_coaching row with {athlete_id=}",
            exc_info=True,
        )

    # clean up the response data
    del response_data["id"]
    del response_data["athlete_id"]
    del response_data["created_at"]
    response_data["training_week"] = json.loads(response_data["training_week"])

    return TrainingWeekWithCoaching(**response_data)


def upsert_training_week_update(
    athlete_id: int,
    mid_week_analysis: MidWeekAnalysis,
    training_week_update_with_planning: TrainingWeekWithPlanning,
) -> APIResponse:
    """Upsert a row into the training_week_update table"""

    row_data = {
        "athlete_id": athlete_id,
        "activities": json.dumps(
            [activity.dict() for activity in mid_week_analysis.activities]
        ),
        "training_week": json.dumps(
            [session.dict() for session in mid_week_analysis.training_week]
        ),
        "planning": training_week_update_with_planning.planning,
        "training_week_update": json.dumps(
            [
                session.dict()
                for session in training_week_update_with_planning.training_week
            ]
        ),
    }

    table = client.table("training_week_update")
    response = table.upsert(row_data).execute()

    return response


def mock_upsert_training_week_update(
    athlete_id: int,
    mid_week_analysis: MidWeekAnalysis,
    training_week_update_with_planning: TrainingWeekWithPlanning,
) -> APIResponse:
    """Mock version of upsert_training_week_update for testing"""

    row_data = {
        "athlete_id": athlete_id,
        "activities": [activity.dict() for activity in mid_week_analysis.activities],
        "training_week": [
            session.dict() for session in mid_week_analysis.training_week
        ],
        "planning": training_week_update_with_planning.planning,
        "training_week_update": [
            session.dict()
            for session in training_week_update_with_planning.training_week
        ],
    }
    print(json.dumps(row_data, indent=4))
    print(f"{mid_week_analysis.miles_ran=}")
    print(f"{training_week_update_with_planning.total_weekly_mileage=}")
    return APIResponse(data=[row_data], count=1)


def get_training_week_update(athlete_id: int) -> TrainingWeekWithPlanning:
    """Get the most recent training_week_update row by athlete_id"""

    table = client.table("training_week_update")
    response = (
        table.select("*")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    try:
        response_data = response.data[0]
    except Exception:
        raise ValueError(
            f"Could not find training_week_update row with {athlete_id=}", exc_info=True
        )

    # clean up the response data
    del response_data["id"]
    del response_data["athlete_id"]
    del response_data["created_at"]
    response_data["activities"] = json.loads(response_data["activities"])
    response_data["training_week"] = json.loads(response_data["training_week"])
    response_data["training_week_update"] = json.loads(
        response_data["training_week_update"]
    )

    return TrainingWeekWithPlanning(**response_data)
