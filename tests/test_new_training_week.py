import json
import os
import random
import statistics
import sys
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

sys.path.append("./")

from src.llm import get_completion_json
from src.supabase_client import list_users
from src.types.training_week import TrainingSession, TrainingWeekWithCoaching
from src.types.user_row import UserRow
from tests.common import run_new_training_week_process_wrapped


class WeeklyMileageAccuracy(BaseModel):
    recommended_weekly_mileage: str = Field(
        description="Short text representation of the recommended weekly mileage"
    )
    error: float = Field(
        description="The absolute error between the recommended and actual weekly mileage"
    )


class NewTrainingWeekError(BaseModel):
    user: UserRow
    """The user that was sampled"""
    recommended_weekly_mileage: str
    """The recommended weekly mileage from the coach"""
    planning: str
    """The planning from the coach"""
    training_week: List[TrainingSession]
    """The training week from the coach"""
    generated_weekly_mileage: float
    """The actual weekly mileage from the training_week"""
    error: float
    """The absolute error between the recommended and actual weekly mileage"""


def get_twwc_accuracy(training_week_with_coaching: TrainingWeekWithCoaching):

    msg = f"""Given the following coaching recommendation: {training_week_with_coaching.weekly_mileage_target}
    How far off is the following week's mileage: {training_week_with_coaching.total_weekly_mileage}"""

    return get_completion_json(
        message=msg,
        response_model=WeeklyMileageAccuracy,
    )


def write_results_to_artifacts(results: list[NewTrainingWeekError]) -> None:
    """
    Store output artifacts locally

    :param results: List of NewTrainingWeekError objects to be written
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    directory = "tests/artifacts/new_training_week_errors"
    os.makedirs(directory, exist_ok=True)

    filename = f"{directory}/{timestamp}.json"

    with open(filename, "w") as f:
        json.dump([result.dict() for result in results], f, indent=2, default=str)

    print(f"Results written to {filename}")


def assess_accuracy(sample_size: int = 10):
    """
    Test the accuracy of the new training week process

    :param sample_size: The number of users to sample
    """
    sampled_users = random.choices(list_users(), k=sample_size)
    results = []
    for i, user in enumerate(sampled_users):
        print(f"({i+1} of {sample_size}) {user.email}")
        twwc = run_new_training_week_process_wrapped(user)
        response = get_twwc_accuracy(twwc)
        results.append(
            NewTrainingWeekError(
                user=user,
                recommended_weekly_mileage=response.recommended_weekly_mileage,
                planning=twwc.planning,
                training_week=twwc.training_week,
                generated_weekly_mileage=twwc.total_weekly_mileage,
                error=response.error,
            )
        )

    write_results_to_artifacts(results)

    errors = [result.error for result in results]
    print(f"Min: {min(errors):.2f}")
    print(f"Mean: {sum(errors) / len(errors):.2f}")
    print(f"Max: {max(errors):.2f}")
    print(f"Stdev: {statistics.stdev(errors):.2f}")


assess_accuracy(sample_size=20)
