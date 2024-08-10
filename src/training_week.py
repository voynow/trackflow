from typing import List

from src.constants import COACH_ROLE
from src.llm import get_completion, get_completion_json
from src.types.day_of_week_summary import DayOfWeekSummary
from src.types.training_week import TrainingWeek
from src.types.training_week_with_coaching import TrainingWeekWithCoaching
from src.types.week_summary import WeekSummary


def get_typical_week_training_review(
    sysmsg_base: str,
    day_of_week_summaries: List[DayOfWeekSummary],
) -> str:
    sysmsg = f"{sysmsg_base} You will be provided summary statistics (aggregated by day of the week) of your client's training over the past several weeks."
    usermsg = (
        str(day_of_week_summaries)
        + "As the coach, provide a very concise training review for your client on their typical week. e.g. Which days are best for their schedule? When do they rest? When (if ever) is their long run? When do they incorporate speed work? Write in paragraph form."
    )
    return get_completion(
        [{"role": "assistant", "content": sysmsg}, {"role": "user", "content": usermsg}]
    )


def get_weekly_mileage_target(
    sysmsg_base: str,
    weekly_summaries: List[WeekSummary],
) -> str:
    sysmsg = f"""{sysmsg_base} You will be provided summary statistics (aggregated by week) of your client's training over the past several weeks."""
    usermsg = f"""Starting from earliest to most recent, here are the weekly summaries:
{weekly_summaries}
As the coach, provide very concise feedback and prescribe your client a target weekly mileage for next week. Be specific and refer to the data provided. Write in paragraph form."""
    return get_completion(
        [{"role": "assistant", "content": sysmsg}, {"role": "user", "content": usermsg}]
    )


def get_training_week(
    sysmsg_base: str,
    typical_week_training_review: str,
    weekly_mileage_target: str,
) -> TrainingWeek:
    message = f"""{sysmsg_base} Here is your review of your client's typical week:
{typical_week_training_review}

Additionally, here is the weekly mileage target you provided:
{weekly_mileage_target}

Build out their next week of training. As a general rule, distribute volume and intensity evenly throughout the week as much as possible."""

    return get_completion_json(
        message=message,
        response_model=TrainingWeek,
    )


def generate_training_week(
    client_preferences: str,
    day_of_week_summaries: List[DayOfWeekSummary],
    weekly_summaries: List[WeekSummary],
) -> TrainingWeekWithCoaching:

    sysmsg_base = f"""{COACH_ROLE}
Your client has included the following preferenced: {client_preferences}
Note: convert pace values where applicable e.g. 7.5 -> 7m 30s"""

    typical_week_training_review = get_typical_week_training_review(
        sysmsg_base=sysmsg_base, day_of_week_summaries=day_of_week_summaries
    )
    weekly_mileage_target = get_weekly_mileage_target(
        sysmsg_base=sysmsg_base, weekly_summaries=weekly_summaries
    )
    training_week = get_training_week(
        sysmsg_base=sysmsg_base,
        typical_week_training_review=typical_week_training_review,
        weekly_mileage_target=weekly_mileage_target,
    )

    return TrainingWeekWithCoaching(
        training_week=training_week,
        typical_week_training_review=typical_week_training_review,
        weekly_mileage_target=weekly_mileage_target,
    )
