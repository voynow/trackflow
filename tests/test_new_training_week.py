import sys

sys.path.append("./")

import json
import os
import random
import statistics
import sys
from datetime import datetime
from typing import Tuple

from freezegun import freeze_time
from pydantic import BaseModel, Field
from stravalib.client import Client

from src.activities import (
    get_activities_df,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.auth_manager import get_strava_client
from src.constants import COACH_ROLE
from src.new_training_week import (
    ensure_completed_set_to_false,
    generate_week,
    get_typical_week_training_review,
    get_weekly_mileage_target,
)
from src.supabase_client import list_users
from src.training_week import standardize_training_week
from src.types.training_week import (
    TrainingWeek,
    TrainingWeekGeneration,
)
from src.types.user_row import UserRow
from src.types.week_summary import WeekSummary


class ExposedDataResponse(BaseModel):
    training_week: TrainingWeek
    training_week_generation: TrainingWeekGeneration
    weekly_summaries: list[WeekSummary]
    coaches_target: str


def expose_training_week_gen(
    user: UserRow,
    date_str: str,
) -> ExposedDataResponse:

    @freeze_time(f"{date_str} 20:30:00")
    def wrapped(user: UserRow, strava_client: Client) -> ExposedDataResponse:
        sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
        activities_df = get_activities_df(strava_client)
        day_of_week_summaries = get_day_of_week_summaries(activities_df)
        weekly_summaries = get_weekly_summaries(activities_df)
        typical_week_training_review = get_typical_week_training_review(
            sysmsg_base=sysmsg_base, day_of_week_summaries=day_of_week_summaries
        )
        coaches_target = get_weekly_mileage_target(
            sysmsg_base=sysmsg_base, weekly_summaries=weekly_summaries
        )
        training_week_generation = generate_week(
            sysmsg_base=sysmsg_base,
            typical_week_training_review=typical_week_training_review,
            coaches_target=coaches_target,
        )

        standardized_training_week = standardize_training_week(
            training_week_generation.training_week
        )

        return ExposedDataResponse(
            training_week=ensure_completed_set_to_false(standardized_training_week),
            training_week_generation=training_week_generation,
            weekly_summaries=weekly_summaries,
            coaches_target=coaches_target,
        )

    strava_client = get_strava_client(user.athlete_id)
    return wrapped(user=user, strava_client=strava_client)


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
    training_week: TrainingWeek
    """The training week from the coach"""
    weekly_summaries: list[WeekSummary]
    """Weekly progress"""
    coaches_target: str
    """The target weekly mileage from the coach"""
    recommended_weekly_mileage: float
    """The recommended weekly mileage from the coach"""
    generated_weekly_mileage: float
    """The actual weekly mileage from the training_week"""
    error: float
    """The absolute error between the recommended and actual weekly mileage"""


def write_results_to_artifacts(results: list) -> None:
    """
    Store output artifacts locally

    :param results: List
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
        response = expose_training_week_gen(
            user=user,
            date_str="2024-09-08",
        )
        results.append(
            NewTrainingWeekError(
                user=user,
                recommended_weekly_mileage=response.training_week_generation.weekly_mileage_target,
                generated_weekly_mileage=response.training_week.total_mileage,
                training_week=response.training_week,
                error=abs(
                    response.training_week_generation.weekly_mileage_target
                    - response.training_week.total_mileage
                ),
                coaches_target=response.coaches_target,
                weekly_summaries=response.weekly_summaries,
            )
        )

    write_results_to_artifacts(results)

    errors = [result.error for result in results]
    print(f"Min: {min(errors):.2f}")
    print(f"Mean: {sum(errors) / len(errors):.2f}")
    print(f"Max: {max(errors):.2f}")
    print(f"Stdev: {statistics.stdev(errors):.2f}")


assess_accuracy(sample_size=20)
