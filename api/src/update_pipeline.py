import logging
from typing import List

from src import supabase_client
from src.activities import (
    get_daily_activity,
    get_weekly_summaries,
)
from src.apn import send_push_notif_wrapper
from src.auth_manager import get_strava_client
from src.constants import COACH_ROLE
from src.llm import get_completion_json
from src.mileage_recommendation import gen_mileage_recommendation
from src.types.activity import DailyMetrics
from src.types.mileage_recommendation import MileageRecommendation
from src.types.training_week import PseudoTrainingWeek, TrainingWeek
from src.types.update_pipeline import ExeType
from src.types.user import Preferences, UserRow
from src.utils import datetime_now_est

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_remaining_days_of_week(today, exe_type: ExeType) -> List[str]:
    """
    Returns the remaining days of the week from the given day's perspective.
    Special handling for Sunday:
    - If it's Sunday and exe_type is ExeType.NEW_WEEK, return the full week starting with Monday
    - If it's Sunday and exe_type is ExeType.MID_WEEK, return an empty list

    :param today: DailyMetrics object representing today's metrics and date
    :param exe_type: The type of update to be generated
    :return: List of remaining days of the week
    """
    days_of_week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    day_index = days_of_week.index(today.day_of_week)

    # on Sunday, we either generate a new week or no remaining days
    if today.day_of_week == "sun":
        if exe_type == ExeType.NEW_WEEK:
            return days_of_week
        else:
            return []

    return days_of_week[day_index + 1 :]


def gen_pseudo_training_week(
    last_n_days_of_activity: List[DailyMetrics],
    mileage_recommendation: MileageRecommendation,
    miles_completed_this_week: float,
    miles_remaining_this_week: float,
    rest_of_week: List[str],
    user_preferences: Preferences,
) -> PseudoTrainingWeek:
    message = f"""{COACH_ROLE}

Your athlete has provided the following preferences:
{user_preferences}

Here is the athlete's activity for the past {len(last_n_days_of_activity)} days:
{last_n_days_of_activity}

The athlete has completed {miles_completed_this_week} miles this week and has {miles_remaining_this_week} miles remaining (if we are halfway through the week and this goal is no longer realistic, that is fine just ensure the athlete finished out the week safely)

Additionally, here are some notes you have written on recommendations for the week in question:
{mileage_recommendation}

Lets generate a pseudo-training week for the next {len(rest_of_week)} days:
{rest_of_week}
"""
    if len(rest_of_week) == 0:
        return PseudoTrainingWeek(days=[])
    return get_completion_json(
        message=message,
        response_model=PseudoTrainingWeek,
    )


def gen_training_week(
    user: UserRow,
    pseudo_training_week: PseudoTrainingWeek,
    mileage_recommendation: MileageRecommendation,
) -> TrainingWeek:
    message = f"""{COACH_ROLE}

Your athlete has provided the following preferences:
{user.preferences}

Here is the pseudo-training week you created for your athlete:
{pseudo_training_week}

Here are some notes you have written on recommendations for the week in question:
{mileage_recommendation}

Please create a proper training week for the next {len(pseudo_training_week.days)} days based on the information provided.
"""
    if len(pseudo_training_week.days) == 0:
        return TrainingWeek(sessions=[])
    return get_completion_json(
        message=message,
        response_model=TrainingWeek,
    )


def update_training_week(user: UserRow, exe_type: ExeType) -> dict:
    """Single function to handle all training week updates"""

    strava_client = get_strava_client(user.athlete_id)
    daily_activity = get_daily_activity(strava_client)
    weekly_summaries = get_weekly_summaries(
        strava_client=strava_client, daily_metrics=daily_activity
    )

    if exe_type == ExeType.NEW_WEEK:
        mileage_recommendation = gen_mileage_recommendation(
            user_preferences=user.preferences,
            weekly_summaries=weekly_summaries,
        )
        supabase_client.insert_mileage_recommendation(
            athlete_id=user.athlete_id,
            mileage_recommendation=mileage_recommendation,
            year=weekly_summaries[-1].year,
            week_of_year=weekly_summaries[-1].week_of_year,
        )
    else:
        mileage_recommendation = supabase_client.get_mileage_recommendation(
            athlete_id=user.athlete_id,
            year=weekly_summaries[-1].year,
            week_of_year=weekly_summaries[-1].week_of_year,
        )

    rest_of_week = get_remaining_days_of_week(daily_activity[-1], exe_type)
    this_weeks_activity = (
        [] if len(rest_of_week) == 7 else daily_activity[-(7 - len(rest_of_week)) :]
    )
    miles_completed_this_week = sum(
        [obj.distance_in_miles for obj in this_weeks_activity]
    )

    pseudo_training_week = gen_pseudo_training_week(
        last_n_days_of_activity=daily_activity[-14:],
        mileage_recommendation=mileage_recommendation,
        miles_completed_this_week=miles_completed_this_week,
        miles_remaining_this_week=mileage_recommendation.total_volume
        - miles_completed_this_week,
        rest_of_week=rest_of_week,
        user_preferences=user.preferences,
    )
    training_week = gen_training_week(
        user=user,
        pseudo_training_week=pseudo_training_week,
        mileage_recommendation=mileage_recommendation,
    )

    supabase_client.upsert_training_week(
        athlete_id=user.athlete_id,
        future_training_week=training_week,
        past_training_week=this_weeks_activity,
    )
    try:
        send_push_notif_wrapper(user)
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return {"success": False}
    return {"success": True}


def update_all_users() -> dict:
    """
    Evenings excluding Sunday: Send update to users who have not yet triggered an update today
    Sunday evening: Send new training week to all active users
    """
    if datetime_now_est().weekday() != 6:
        for user in supabase_client.list_users():
            if not supabase_client.has_user_updated_today(user.athlete_id):
                update_training_week(user, ExeType.MID_WEEK)
    else:
        for user in supabase_client.list_users():
            update_training_week(user, ExeType.NEW_WEEK)
    return {"success": True}
