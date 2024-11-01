from datetime import datetime, timedelta
from typing import Callable, List

from freezegun import freeze_time
from stravalib.client import Client

from src.auth_manager import get_strava_client
from src.update_pipeline import (
    mid_week_update_pipeline_test,
    new_training_week_pipeline,
    training_week_update_pipeline,
)
from src.supabase_client import upsert_training_week_test
from src.types.training_week import TrainingWeek
from src.types.user_row import UserRow


def gen_helper(
    mock_user: UserRow,
    date_str: str,
    func: Callable[[UserRow, Client], TrainingWeek],
) -> TrainingWeek:
    @freeze_time(f"{date_str} 20:30:00")
    def wrapped(user: UserRow) -> TrainingWeek:
        training_week = training_week_update_pipeline(
            user=user,
            pipeline_function=func,
            upsert_training_week=upsert_training_week_test,
        )
        return training_week

    get_strava_client(mock_user.athlete_id)
    return wrapped(user=mock_user)


def walk_through_week(
    mock_user: UserRow,
    start_date: str,
) -> List[TrainingWeek]:
    """Walk throug the week from start date."""

    # validate that the start date is a Sunday
    if datetime.strptime(start_date, "%Y-%m-%d").weekday() != 6:
        raise ValueError("Start date must be a Sunday")

    training_weeks = []
    for i in range(7):
        current_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        if i == 0:
            training_weeks.append(
                gen_helper(
                    mock_user=mock_user,
                    date_str=date_str,
                    func=new_training_week_pipeline,
                )
            )
        else:
            training_weeks.append(
                gen_helper(
                    mock_user=mock_user,
                    date_str=date_str,
                    func=mid_week_update_pipeline_test,
                )
            )
    return training_weeks
