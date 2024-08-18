from typing import List

from src.llm import get_completion, get_completion_json
from src.types.day_of_week_summary import DayOfWeekSummary
from src.types.training_week import (
    TrainingWeekWithCoaching,
    TrainingWeekWithPlanning,
)
from src.types.week_summary import WeekSummary


def get_typical_week_training_review(
    sysmsg_base: str,
    day_of_week_summaries: List[DayOfWeekSummary],
) -> str:
    sysmsg = f"{sysmsg_base}\nYou will be provided summary statistics (aggregated by day of the week) of your client's training over the past several weeks."
    usermsg = f"""{day_of_week_summaries}
As the coach, write a review for your client on their typical week. e.g. Which days are best for their schedule? When do they rest? When (if ever) is their long run? When do they incorporate speed work? Write 1-2 sentences while being as concise as possible."""
    return get_completion(
        [{"role": "assistant", "content": sysmsg}, {"role": "user", "content": usermsg}]
    )


def get_weekly_mileage_target(
    sysmsg_base: str,
    weekly_summaries: List[WeekSummary],
) -> str:
    sysmsg = f"""{sysmsg_base}\nYou will be provided summary statistics (aggregated by week) of your client's training over the past several weeks."""
    usermsg = f"""Starting from earliest to most recent, here are the weekly summaries:
{weekly_summaries}
As the coach, prescribe your client a target weekly mileage and long run range for next week. Be specific and refer to the data provided. Write 2-3 sentences while being as concise as possible."""
    return get_completion(
        [{"role": "assistant", "content": sysmsg}, {"role": "user", "content": usermsg}]
    )


def get_training_week(
    sysmsg_base: str,
    typical_week_training_review: str,
    weekly_mileage_target: str,
) -> TrainingWeekWithPlanning:
    message = f"""{sysmsg_base}\nHere is your review of your client's typical week:
{typical_week_training_review}

Additionally, here is the weekly mileage target you provided:
{weekly_mileage_target}

Build out their next week of training."""
    return get_completion_json(
        message=message,
        response_model=TrainingWeekWithPlanning,
    )


def generate_training_week(
    sysmsg_base: str,
    day_of_week_summaries: List[DayOfWeekSummary],
    weekly_summaries: List[WeekSummary],
) -> TrainingWeekWithCoaching:
    typical_week_training_review = get_typical_week_training_review(
        sysmsg_base=sysmsg_base, day_of_week_summaries=day_of_week_summaries
    )
    weekly_mileage_target = get_weekly_mileage_target(
        sysmsg_base=sysmsg_base, weekly_summaries=weekly_summaries
    )
    training_week_with_planning = get_training_week(
        sysmsg_base=sysmsg_base,
        typical_week_training_review=typical_week_training_review,
        weekly_mileage_target=weekly_mileage_target,
    )

    return TrainingWeekWithCoaching(
        training_week_planning=training_week_with_planning.planning,
        training_week=training_week_with_planning.training_week,
        typical_week_training_review=typical_week_training_review,
        weekly_mileage_target=weekly_mileage_target,
    )
