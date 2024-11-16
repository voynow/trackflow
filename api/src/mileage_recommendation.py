from typing import List

from src.constants import COACH_ROLE
from src.llm import get_completion_json
from src.types.activity import WeekSummary
from src.types.mileage_recommendation import MileageRecommendation
from src.types.user import Preferences


def get_mileage_recommendation(
    user_preferences: Preferences,
    weekly_summaries: List[WeekSummary],
) -> MileageRecommendation:

    message = f"""{COACH_ROLE}

Your athlete has provided the following preferences: {user_preferences}

Here is a summary of the athlete's training for the past {len(weekly_summaries)} weeks:
{weekly_summaries}

Your task is to provide training recommendations for the upcoming week."""

    mileage_recommendation = get_completion_json(
        message=message,
        response_model=MileageRecommendation,
    )

    return mileage_recommendation
