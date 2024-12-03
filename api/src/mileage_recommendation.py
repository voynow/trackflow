import logging
from typing import List

from src import activities, supabase_client
from src.constants import COACH_ROLE
from src.llm import get_completion_json
from src.training_plan import gen_training_plan_pipeline
from src.types.activity import DailyMetrics, WeekSummary
from src.types.mileage_recommendation import (
    MileageRecommendation,
    MileageRecommendationRow,
)
from src.types.update_pipeline import ExeType
from src.types.user import Preferences, UserRow
from src.utils import datetime_now_est

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def gen_mileage_rec_wrapper(
    user: UserRow, weekly_summaries: List[WeekSummary]
) -> MileageRecommendation:
    """
    Abstraction for mileage rec generation, either pulled from training plan
    generation or generated directly from weekly summaries

    :param user: UserRow object
    :param weekly_summaries: List of WeekSummary objects
    :return: MileageRecommendation used to generate training week
    """
    if datetime_now_est().weekday() != 6:
        raise ValueError(
            "Mileage recommendation can only be generated on Sunday (night) when the week is complete"
        )
    if user.preferences.race_date and user.preferences.race_distance:
        training_plan = gen_training_plan_pipeline(
            user=user, weekly_summaries=weekly_summaries
        )
        next_week_plan = training_plan.training_week_plans[0]
        return MileageRecommendation(
            thoughts=next_week_plan.notes,
            total_volume=next_week_plan.total_distance,
            long_run=next_week_plan.long_run_distance,
        )
    else:
        return gen_mileage_recommendation(
            user_preferences=user.preferences,
            weekly_summaries=weekly_summaries,
        )


def create_new_mileage_recommendation(
    user: UserRow, weekly_summaries: List[WeekSummary]
) -> MileageRecommendation:
    """
    Creates a new mileage recommendation for the next week

    :param user: user entity
    :param weekly_summaries: list of weekly summaries
    :return: mileage recommendation entity
    """
    past_week = weekly_summaries[-1].week_of_year
    past_year = weekly_summaries[-1].year

    if past_week == 52:
        next_week = 1
        next_year = past_year + 1
    else:
        next_week = past_week + 1
        next_year = past_year

    mileage_recommendation = gen_mileage_rec_wrapper(
        user=user, weekly_summaries=weekly_summaries
    )
    supabase_client.insert_mileage_recommendation(
        MileageRecommendationRow(
            week_of_year=next_week,
            year=next_year,
            thoughts=mileage_recommendation.thoughts,
            total_volume=mileage_recommendation.total_volume,
            long_run=mileage_recommendation.long_run,
            athlete_id=user.athlete_id,
        )
    )
    return mileage_recommendation


def get_or_gen_mileage_recommendation(
    user: UserRow,
    daily_activity: List[DailyMetrics],
    exe_type: ExeType,
) -> MileageRecommendation:
    """
    Executes mileage rec strategy depending on exe type

    :param user: user entity
    :param daily_activity: list of daily metrics
    :param exe_type: new week or mid week
    :return: mileage recommendation entity
    """
    weekly_summaries = activities.get_weekly_summaries(daily_metrics=daily_activity)

    if exe_type == ExeType.NEW_WEEK:
        return create_new_mileage_recommendation(
            user=user, weekly_summaries=weekly_summaries
        )
    else:
        mileage_recommendation_row = supabase_client.get_mileage_recommendation(
            athlete_id=user.athlete_id,
            year=weekly_summaries[-1].year,
            week_of_year=weekly_summaries[-1].week_of_year,
        )
        return MileageRecommendation(
            thoughts=mileage_recommendation_row.thoughts,
            total_volume=mileage_recommendation_row.total_volume,
            long_run=mileage_recommendation_row.long_run,
        )
