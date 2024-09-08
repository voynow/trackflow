from src.llm import get_completion_json
from src.training_week import ensure_completed_set_to_false, standardize_training_week
from src.types.activity_summary import ActivitySummary
from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import (
    TrainingWeek,
    TrainingWeekWithPlanning,
)


def generate_completed_training_week(
    sysmsg_base: str,
    completed_activities: list[ActivitySummary],
) -> TrainingWeek:
    msg = (
        sysmsg_base
        + f"""\nHere is your client's progress so far this week:
{completed_activities}

Extract a valid TrainingWeek from the above information, denoting each session as completed.
"""
    )
    return get_completion_json(
        message=msg,
        response_model=TrainingWeek,
    )


def generate_rest_of_week_with_planning(
    sysmsg_base: str,
    mid_week_analysis: MidWeekAnalysis,
) -> TrainingWeekWithPlanning:
    msg = (
        sysmsg_base
        + f"""\nThe original plan for this week targeted {mid_week_analysis.miles_target} miles. Your client has run {mid_week_analysis.miles_ran} miles so far (and they have {mid_week_analysis.miles_remaining} miles left to run this week), but the plan for the rest of the week includes {mid_week_analysis.future_miles_planned} miles. Adjust the plan accordingly given the following information:

Here is your client's progress so far this week:
{mid_week_analysis.completed_training_week}

Here is the plan for the rest of the week:
{mid_week_analysis.training_week_future}

What changes need to be made so that your client runs {mid_week_analysis.miles_remaining} more miles this week? Try not to alter the long run distance if possible. Response with the remaining days only."""
    )

    return get_completion_json(
        message=msg,
        response_model=TrainingWeekWithPlanning,
    )


def join_training_weeks(
    completed_training_week: TrainingWeek,
    rest_of_week: TrainingWeek,
) -> TrainingWeek:
    """
    Join the original training week with the rest of the week with planning

    :param original_training_week: Original training week
    :param rest_of_week_with_planning: Rest of the week with planning
    :return: Training week
    """
    sessions = []
    for session in completed_training_week.sessions:
        if session.completed:
            sessions.append(session)
    for session in rest_of_week.sessions:
        sessions.append(session)
    return TrainingWeek(sessions=sessions)


def generate_mid_week_update(
    sysmsg_base: str,
    training_week: TrainingWeek,
    completed_activities: list[ActivitySummary],
) -> TrainingWeek:
    """
    Generate update + post-processing

    :param sysmsg_base: Base message for the LLM
    :param mid_week_analysis: Mid-week analysis data
    :return: Training week
    """
    completed_training_week = generate_completed_training_week(
        sysmsg_base=sysmsg_base,
        completed_activities=completed_activities,
    )

    mid_week_analysis = MidWeekAnalysis(
        completed_training_week=completed_training_week,
        original_training_week=training_week,
    )

    rest_of_week_with_planning = generate_rest_of_week_with_planning(
        sysmsg_base=sysmsg_base,
        mid_week_analysis=mid_week_analysis,
    )

    rest_of_training_week = ensure_completed_set_to_false(
        rest_of_week_with_planning.training_week
    )

    full_training_week = join_training_weeks(
        completed_training_week=completed_training_week,
        rest_of_week=rest_of_training_week,
    )

    return standardize_training_week(full_training_week)
