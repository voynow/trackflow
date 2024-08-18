from src.llm import get_completion_json
from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import TrainingWeekWithPlanning


def get_updated_training_week(
    sysmsg_base: str,
    mid_week_analysis: MidWeekAnalysis,
) -> TrainingWeekWithPlanning:
    msg = (
        sysmsg_base
        + f"""\nThe original plan for this week targeted {mid_week_analysis.miles_target} miles. Your client has run {mid_week_analysis.miles_ran} miles so far (and they have {mid_week_analysis.miles_remaining} miles left to run this week), but the plan for the rest of the week includes {mid_week_analysis.future_miles_planned} miles. Adjust the plan accordingly given the following information:

Here is your client's progress so far this week:
{mid_week_analysis.activities}

Here is the plan for the rest of the week:
{mid_week_analysis.training_week_future}

What changes need to be made so that your client runs {mid_week_analysis.miles_remaining} more miles this week?"""
    )

    return get_completion_json(
        message=msg,
        response_model=TrainingWeekWithPlanning,
    )
