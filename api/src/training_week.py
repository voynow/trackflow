from datetime import timedelta
from typing import List

from src.constants import COACH_ROLE
from src.llm import get_completion, get_completion_json
from src.prompts import (
    COACHES_NOTES_PROMPT,
    PSEUDO_TRAINING_WEEK_PROMPT,
    TRAINING_WEEK_PROMPT,
)
from src.types.activity import DailyMetrics
from src.types.mileage_recommendation import MileageRecommendation
from src.types.training_week import (
    EnrichedActivity,
    FullTrainingWeek,
    PseudoTrainingWeek,
    TrainingWeek,
)
from src.types.update_pipeline import ExeType
from src.types.user import Preferences, UserRow


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
    message = PSEUDO_TRAINING_WEEK_PROMPT.substitute(
        COACH_ROLE=COACH_ROLE,
        user_preferences=user_preferences,
        n_days=len(last_n_days_of_activity),
        last_n_days_of_activity=last_n_days_of_activity,
        miles_completed_this_week=miles_completed_this_week,
        miles_remaining_this_week=miles_remaining_this_week,
        mileage_recommendation=mileage_recommendation,
        n_remaining_days=len(rest_of_week),
        rest_of_week=rest_of_week,
    )
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
    message = TRAINING_WEEK_PROMPT.substitute(
        COACH_ROLE=COACH_ROLE,
        preferences=user.preferences,
        n_days=len(pseudo_training_week.days),
        pseudo_training_week=pseudo_training_week,
        mileage_recommendation=mileage_recommendation,
    )
    if len(pseudo_training_week.days) == 0:
        return TrainingWeek(sessions=[])
    return get_completion_json(
        message=message,
        response_model=TrainingWeek,
    )


def gen_coaches_notes(
    activity_of_interest: DailyMetrics, past_7_days: List[DailyMetrics]
) -> str:
    message = COACHES_NOTES_PROMPT.substitute(
        COACH_ROLE=COACH_ROLE,
        past_7_days=past_7_days,
        activity_of_interest=activity_of_interest,
        day_of_week=activity_of_interest.day_of_week,
    )
    return get_completion(message=message)


def slice_and_gen_weekly_activity(
    daily_activity: List[DailyMetrics], rest_of_week: List[str]
) -> List[EnrichedActivity]:
    """
    Slices the weekly activity based on the remaining days of the week and
    generates coach notes for each activity

    :param daily_activity: List of DailyMetrics objects
    :param rest_of_week: List of remaining days of the week
    :return: List of EnrichedActivity objects
    """
    if len(rest_of_week) == 7:
        this_weeks_activity = []
    else:
        this_weeks_activity = daily_activity[-(7 - len(rest_of_week)) :]

    enriched_activities = []
    for activity_of_interest in this_weeks_activity:
        past_7_days = [
            obj
            for obj in daily_activity
            if obj.date > activity_of_interest.date - timedelta(days=7)
            and obj.date < activity_of_interest.date
        ]
        coaches_notes = gen_coaches_notes(
            activity_of_interest=activity_of_interest, past_7_days=past_7_days
        )
        enriched_activities.append(
            EnrichedActivity(activity=activity_of_interest, coaches_notes=coaches_notes)
        )
    return enriched_activities


def gen_full_training_week(
    user: UserRow,
    daily_activity: List[DailyMetrics],
    mileage_rec: MileageRecommendation,
    exe_type: ExeType,
) -> FullTrainingWeek:
    """
    Generates full training week given mileage recommendation

    :param user: user entity
    :param daily_activity: list of daily actvity metrics past n weeks
    :param mileage_rec: recommendation for this weeks training
    :param exe_type: new week or mid week
    :return: full training week
    """
    rest_of_week = get_remaining_days_of_week(daily_activity[-1], exe_type)
    this_weeks_activity = slice_and_gen_weekly_activity(daily_activity, rest_of_week)
    miles_completed_this_week = sum(
        [obj.activity.distance_in_miles for obj in this_weeks_activity]
    )
    miles_remaining_this_week = mileage_rec.total_volume - miles_completed_this_week
    pseudo_training_week = gen_pseudo_training_week(
        last_n_days_of_activity=daily_activity[-14:],
        mileage_recommendation=mileage_rec,
        miles_completed_this_week=miles_completed_this_week,
        miles_remaining_this_week=miles_remaining_this_week,
        rest_of_week=rest_of_week,
        user_preferences=user.preferences,
    )
    training_week = gen_training_week(
        user=user,
        pseudo_training_week=pseudo_training_week,
        mileage_recommendation=mileage_rec,
    )
    return FullTrainingWeek(
        past_training_week=this_weeks_activity,
        future_training_week=training_week,
    )
