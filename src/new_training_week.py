import logging
from typing import List

from src.llm import get_completion, get_completion_json
from src.training_week import standardize_training_week
from src.types.activity import WeekSummary
from src.types.day_of_week_summary import DayOfWeekSummary
from src.types.training_week import (
    TrainingSession,
    TrainingWeek,
    TrainingWeekGeneration,
    TrainingWeekWithPlanning,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
As the coach, prescribe your client a target weekly mileage and long run range for next week. Be specific and refer to the data provided. Write 3-4 sentences while being as concise as possible."""
    return get_completion(
        [{"role": "assistant", "content": sysmsg}, {"role": "user", "content": usermsg}]
    )


def get_training_week_with_planning(
    sysmsg_base: str,
    typical_week_training_review: str,
    weekly_mileage_target: str,
) -> TrainingWeekWithPlanning:
    message = f"""{sysmsg_base}\nHere is your review of your client's typical week:
{typical_week_training_review}

Additionally, here is the weekly mileage target you provided:
{weekly_mileage_target}

Build out their next week of training. Distribute volume and intensity evenly throughout the week. You must adhere to the weekly mileage target and long run range."""
    return get_completion_json(
        message=message,
        response_model=TrainingWeekWithPlanning,
    )


def initial_week_generation(
    sysmsg_base: str,
    coaches_target: str,
) -> TrainingWeekGeneration:
    message = f"""{sysmsg_base}

Some thoughts on your client's weekly mileage target:
{coaches_target}

Build out their next week of training. Distribute volume and intensity evenly throughout the week. You must adhere to the weekly mileage target and long run range."""
    return get_completion_json(
        message=message,
        response_model=TrainingWeekGeneration,
    )


def retry_week_generation(
    sysmsg_base: str,
    coaches_target: str,
    weekly_mileage_target: float,
    actual_mileage: float,
    previous_training_week: TrainingWeek,
) -> TrainingWeekGeneration:
    message = f"""{sysmsg_base}

Some thoughts on your client's weekly mileage target:
{coaches_target}

The previous training week you generated had a total mileage of {actual_mileage}, which did not meet the target of {weekly_mileage_target} (within 5%).

For inspiration, here is the previous training week you generated:
{previous_training_week}

Please regenerate the week, adjusting volume and intensity to ensure the total mileage is closer to the target while still balancing intensity throughout the week."""

    return get_completion_json(
        message=message,
        response_model=TrainingWeekGeneration,
    )


def is_mileage_within_target(actual: float, target: float) -> bool:
    """
    Check if the actual mileage is within the target range

    :param actual: The actual mileage achieved
    :param target: The target mileage
    :return: True if the actual mileage is within the target range, False otherwise
    """
    if 0.95 * target < actual < 1.05 * target:
        return True
    if abs(actual - target) <= 1.5:
        return True
    return False


def generate_week(
    sysmsg_base: str,
    coaches_target: str,
) -> TrainingWeekGeneration:
    """
    Generate a training week, retrying up to max_retries times if the total mileage
    is not within acceptable range of the target. Returns the best attempt.

    :param sysmsg_base: Base system message for the LLM
    :param coaches_target: Coach's target for the week
    :return: TrainingWeekGeneration: The best generated training week
    """
    max_retries = 3
    best_attempt = None
    best_difference = float("inf")

    for attempt in range(max_retries):
        if attempt == 0:
            training_week_generation = initial_week_generation(
                sysmsg_base=sysmsg_base,
                coaches_target=coaches_target,
            )
        else:
            training_week_generation = retry_week_generation(
                sysmsg_base=sysmsg_base,
                coaches_target=coaches_target,
                weekly_mileage_target=training_week_generation.weekly_mileage_target,
                actual_mileage=training_week_generation.training_week.total_mileage,
                previous_training_week=training_week_generation.training_week,
            )

        current_difference = abs(
            training_week_generation.training_week.total_mileage
            - training_week_generation.weekly_mileage_target
        )

        if current_difference < best_difference:
            best_attempt = training_week_generation
            best_difference = current_difference

        is_within_target = is_mileage_within_target(
            actual=training_week_generation.training_week.total_mileage,
            target=training_week_generation.weekly_mileage_target,
        )
        if is_within_target:
            return training_week_generation

        logger.info(
            f"Gen week attempt {attempt + 1}/{max_retries}: total_mileage={training_week_generation.training_week.total_mileage}, "
            f"weekly_mileage_target={training_week_generation.weekly_mileage_target}, difference={current_difference}"
        )

    return best_attempt


def ensure_completed_set_to_false(
    training_week: TrainingWeek,
) -> TrainingWeek:
    """
    Ensure that the completed field is set to False for all sessions
    """
    return TrainingWeek(
        sessions=[
            TrainingSession(
                day=session.day,
                session_type=session.session_type,
                distance=session.distance,
                notes=session.notes,
                completed=False,
            )
            for session in training_week.sessions
        ]
    )


def generate_new_training_week(
    sysmsg_base: str,
    weekly_summaries: List[WeekSummary],
) -> TrainingWeek:
    coaches_target = get_weekly_mileage_target(
        sysmsg_base=sysmsg_base, weekly_summaries=weekly_summaries
    )
    training_week_with_planning = generate_week(
        sysmsg_base=sysmsg_base,
        coaches_target=coaches_target,
    )

    standardized_training_week = standardize_training_week(
        training_week_with_planning.training_week
    )
    return ensure_completed_set_to_false(standardized_training_week)
