from typing import List

from src.constants import COACH_ROLE
from src.llm import get_completion_json
from src.types.activity import WeekSummary
from src.types.mileage_recommendation import MileageRecommendation
from src.types.user import Preferences
from src.utils import datetime_now_est


def gen_mileage_recommendation(
    user_preferences: Preferences,
    weekly_summaries: List[WeekSummary],
) -> MileageRecommendation:
    """
    Recommend a mileage target for total volume and long run

    This should only be called on Sunday night. If called mid-week, recs will
    break due to the current weekly summary not being complete.

    :param weekly_summaries: The athlete's weekly summaries
    :return: A MileageRecommendation
    """
    if datetime_now_est().weekday() != 6:
        raise ValueError(
            "Mileage recommendation can only be generated on Sunday (night) when the week is complete"
        )

    weekly_summaries_str = "\n".join([str(week) for week in weekly_summaries])

    message = f"""{COACH_ROLE}

Your athlete has provided the following preferences: {user_preferences}

Here is a summary of the athlete's training for the past {len(weekly_summaries)} weeks (in reverse chronological order):
{weekly_summaries_str}

Your task is to provide training recommendations for the upcoming week."""

    return get_completion_json(
        message=message,
        response_model=MileageRecommendation,
    )
