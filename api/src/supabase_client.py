import datetime
import os
from typing import List, Optional
from uuid import uuid4

import orjson
from dotenv import load_dotenv
from src.types.activity import DailyMetrics
from src.types.mileage_recommendation import (
    MileageRecommendationRow,
)
from src.types.training_plan import TrainingPlan, TrainingPlanWeekRow
from src.types.training_week import (
    EnrichedActivity,
    FullTrainingWeek,
    TrainingSession,
    TrainingWeek,
)
from src.types.user import Preferences, UserAuthRow, UserRow
from supabase import Client, create_client

load_dotenv()


def init() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)


client = init()


def get_training_week_table_name() -> str:
    """
    Inject test_training_week table name during testing

    :return: The name of the training_week table
    """
    if os.environ.get("TEST_FLAG", "false") == "true":
        return "test_training_week"
    return "training_week"


def get_mileage_recommendation_table_name() -> str:
    """
    Inject test_mileage_recommendation table name during testing

    :return: The name of the mileage_recommendation table
    """
    if os.environ.get("TEST_FLAG", "false") == "true":
        return "test_mileage_recommendation"
    return "mileage_recommendation"


def get_training_plan_table_name() -> str:
    """
    Inject test_training_plan table name during testing

    :return: The name of the training_plan table
    """
    if os.environ.get("TEST_FLAG", "false") == "true":
        return "test_training_plan"
    return "training_plan"


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


def list_users(debug: bool = False) -> list[UserRow]:
    """
    List all users in the user_auth table

    :return: list of UserAuthRow
    """
    table = client.table("user")
    response = table.select("*").execute()

    users = [UserRow(**row) for row in response.data]

    if debug:
        users = [
            user
            for user in users
            if user.email
            in [
                "rachel.decker122@gmail.com",
                "voynow99@gmail.com",
                "voynowtestaddress@gmail.com",
            ]
        ]
    return users


def list_user_auths() -> list[UserAuthRow]:
    """
    List all user_auths in the user_auth table

    :return: list of UserAuthRow
    """
    table = client.table("user_auth")
    response = table.select("*").execute()
    return [UserAuthRow(**row) for row in response.data]


def list_mileage_recommendations() -> list[MileageRecommendationRow]:
    """
    List all mileage_recommendations in the mileage_recommendation table

    :return: list of MileageRecommendationRow
    """
    table = client.table(get_mileage_recommendation_table_name())
    response = table.select("*").execute()
    return [MileageRecommendationRow(**row) for row in response.data]


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


def get_training_week(athlete_id: int) -> FullTrainingWeek:
    """
    Get the most recent training_week row by athlete_id.

    :param athlete_id: int
    :return: FullTrainingWeek
    """
    table = client.table(get_training_week_table_name())
    response = (
        table.select("future_training_week, past_training_week")
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
        future_json_data = orjson.loads(response.data[0]["future_training_week"])
        past_json_data = orjson.loads(response.data[0]["past_training_week"])

        # temp requirement to remove legacy moderate run
        future_json_data_cleansed = []
        for session in future_json_data:
            if session["session_type"] == "moderate run":
                session["session_type"] = "easy run"
            future_json_data_cleansed.append(session)

        return FullTrainingWeek(
            past_training_week=[EnrichedActivity(**obj) for obj in past_json_data],
            future_training_week=TrainingWeek(
                sessions=[
                    TrainingSession(**session) for session in future_json_data_cleansed
                ]
            ),
        )
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
    future_training_week: TrainingWeek,
    past_training_week: List[EnrichedActivity],
):
    """
    Upsert a row into the training_week table

    :param athlete_id: The athlete's ID
    :param future_training_week: Training week data for future sessions
    :param past_training_week: List of daily metrics from past training
    """
    future_sessions = [session.dict() for session in future_training_week.sessions]
    past_sessions = [obj.dict() for obj in past_training_week]
    row_data = {
        "athlete_id": athlete_id,
        "future_training_week": orjson.dumps(future_sessions).decode("utf-8"),
        "past_training_week": orjson.dumps(past_sessions).decode("utf-8"),
    }
    table = client.table(get_training_week_table_name())
    table.upsert(row_data).execute()


def has_user_updated_today(athlete_id: int) -> bool:
    """
    Check if the user has received an update today. Where "today" is defined as
    within the past 23 hours and 30 minutes (to account for any delays in
    yesterday's evening update).

    :param athlete_id: The ID of the athlete
    :return: True if the user has received an update today, False otherwise
    """
    table = client.table(get_training_week_table_name())
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


def insert_mileage_recommendation(mileage_recommendation_row: MileageRecommendationRow):
    """
    Insert a row into the mileage_recommendations table

    :param mileage_recommendation_row: A MileageRecommendationRow object
    """
    print(mileage_recommendation_row.dict())
    table = client.table(get_mileage_recommendation_table_name())
    table.insert(mileage_recommendation_row.dict()).execute()


def get_mileage_recommendation(
    athlete_id: int, dt: datetime.datetime
) -> MileageRecommendationRow:
    """
    Get the most recent mileage recommendation for the given year and week of year

    :param athlete_id: The ID of the athlete
    :param year: The year of the recommendation
    :param week_of_year: The week of the year of the recommendation
    :return: A MileageRecommendation object
    """
    table = client.table(get_mileage_recommendation_table_name())
    response = (
        table.select("*")
        .eq("athlete_id", athlete_id)
        .eq("year", dt.year)
        .eq("week_of_year", dt.isocalendar()[1])
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise ValueError(
            f"Could not find mileage recommendation for {athlete_id=}, year={dt.year}, week={dt.isocalendar()[1]}"
        )
    return MileageRecommendationRow(**response.data[0])


def insert_training_plan(athlete_id: int, training_plan: TrainingPlan):
    """
    Insert a training plan into the training_plan table

    :param athlete_id: The ID of the athlete
    :param training_plan: A TrainingPlan object
    """
    plan_id = str(uuid4())
    table = client.table(get_training_plan_table_name())
    for week in training_plan.training_plan_weeks:
        row = {"athlete_id": athlete_id, "plan_id": plan_id, **week.dict()}
        try:
            TrainingPlanWeekRow(**row)
        except Exception as e:
            raise ValueError(f"Invalid training plan week: {row=}, {e=}")
        table.insert(row).execute()


def get_training_plan(athlete_id: int) -> TrainingPlan:
    """
    Get the most recent training plan for a specific athlete.
    Since new training plan rows are added weekly, we need to get the latest set
    based on created_at timestamp.

    :param athlete_id: The ID of the athlete
    :return: A TrainingPlan object containing the most recent set of training weeks
    """
    table = client.table(get_training_plan_table_name())

    # First get the most recent created_at timestamp for this athlete
    latest_timestamp = (
        table.select("plan_id")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not latest_timestamp.data:
        raise ValueError(f"Could not find training plan for athlete_id {athlete_id}")

    response = (
        table.select("*")
        .eq("athlete_id", athlete_id)
        .eq("plan_id", latest_timestamp.data[0]["plan_id"])
        .order("week_number")
        .execute()
    )

    training_weeks = [TrainingPlanWeekRow(**row) for row in response.data]
    return TrainingPlan(training_plan_weeks=training_weeks)
