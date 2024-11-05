from src.llm import get_completion_json
from src.training_week import standardize_training_week
from src.types.activity import ActivitySummary
from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import (
    TrainingSession,
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

Extract a valid TrainingWeek from the activities provided ONLY (do not make any assumptions on future sessions), denoting each session as completed.
"""
    )
    return get_completion_json(
        message=msg,
        response_model=TrainingWeek,
    )


def rest_of_week_planning_post_processing(
    completed_training_week: TrainingWeek,
    rest_of_training_week: TrainingWeek,
) -> TrainingWeek:
    """
    Ensure rest of week does not overlap with completed training week and
    completion status set to False
    """
    rest_of_week_sessions = []
    for session in rest_of_training_week.sessions:
        if session.day not in [s.day for s in completed_training_week.sessions]:
            rest_of_week_sessions.append(session)

    return TrainingWeek(
        sessions=[
            TrainingSession(
                day=session.day,
                session_type=session.session_type,
                distance=session.distance,
                notes=session.notes,
                completed=False,
            )
            for session in rest_of_week_sessions
        ]
    )


def generate_rest_of_training_week(
    sysmsg_base: str,
    mid_week_analysis: MidWeekAnalysis,
) -> TrainingWeek:
    """
    Generate rest of week training

    :param sysmsg_base: Base message for the LLM
    :param mid_week_analysis: Mid-week analysis data
    :return: TrainingWeek for rest of week ONLY
    """
    msg = (
        sysmsg_base
        + f"""\nThe original plan for this week targeted {mid_week_analysis.miles_target} miles. Your client has run {mid_week_analysis.miles_ran} miles so far (and they have {mid_week_analysis.miles_remaining} miles left to run this week), but the plan for the rest of the week includes {mid_week_analysis.future_miles_planned} miles. Adjust the plan accordingly given the following information:

Here is your client's progress so far this week:
{mid_week_analysis.completed_training_week}

Here is the plan for the remainder of the week:
{mid_week_analysis.training_week_future}

What changes need to be made so that your client runs {mid_week_analysis.miles_remaining} more miles this week?

Rule: 1. Keep the long run constant. This is non-negotiable. 2. There should be no duplicate days in the TrainingWeek sessions."""
    )

    rest_of_week_with_planning = get_completion_json(
        message=msg,
        response_model=TrainingWeekWithPlanning,
    )

    return rest_of_week_planning_post_processing(
        completed_training_week=mid_week_analysis.completed_training_week,
        rest_of_training_week=rest_of_week_with_planning.training_week,
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

    rest_of_training_week = generate_rest_of_training_week(
        sysmsg_base=sysmsg_base,
        mid_week_analysis=mid_week_analysis,
    )

    full_training_week = join_training_weeks(
        completed_training_week=completed_training_week,
        rest_of_week=rest_of_training_week,
    )

    standardized_training_week = standardize_training_week(full_training_week)

    return standardized_training_week
