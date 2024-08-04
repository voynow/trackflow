from typing import List

from src.llm import get_completion, get_completion_json
from src.types.day_of_week_summary import DayOfWeekSummary
from src.types.training_week import TrainingWeek
from src.types.training_week_skeleton import TrainingWeekSkeleton
from src.types.week_summary import WeekSummary
from src.types.weekly_mileage_target_response import WeeklyMileageTargetResponse


def get_typical_training_week_verbose(
    day_of_week_summaries: List[DayOfWeekSummary],
) -> str:
    sysmsg = "You are a talented running coach with years of experience. Your client is training for a marathon. You will be provided summary statistics (aggregated by day of the week) of your client's training over the past several weeks."
    usermsg = (
        str(day_of_week_summaries)
        + "As the coach, provide an analysis estimating what a typical week of training looks like for your client. e.g. Which days are best for their schedule? When do they rest? When (if ever) is their long run? When do they incorporate speed work? Be concice yet thorough."
    )
    return get_completion(
        [{"role": "assistant", "content": sysmsg}, {"role": "user", "content": usermsg}]
    )


def get_training_week_skeleton(training_week_verbose: str) -> TrainingWeekSkeleton:
    message = f"""You are a talented running coach with years of experience. Your client is training for a marathon. Here is an analysis this client's training over the past several weeks:
{training_week_verbose}

Create a training week skeleton for your client. Optimize the schedule for their success, making sure to prioritize rest and recovery around their hardest workouts. As a general rule, lets aim for 1 long run, 1 speed workout, and at least 1 rest day per week."""

    return get_completion_json(
        message=message,
        response_model=TrainingWeekSkeleton,
    )


def get_weekly_mileage_target(
    weekly_summaries: List[WeekSummary],
) -> WeeklyMileageTargetResponse:
    message = f"""You are a talented running coach with years of experience. Your client is training for a marathon. Here are summary statistics (aggregated by week) of your client's training over the past several weeks:
{weekly_summaries}

As the coach, provide some information to your client about weekly mileage targets."""

    return get_completion_json(
        message=message,
        response_model=WeeklyMileageTargetResponse,
    )


def get_training_week(
    training_week_skeleton: TrainingWeekSkeleton,
    weekly_mileage_target: WeeklyMileageTargetResponse,
) -> TrainingWeek:
    message = f"""You are a talented running coach with years of experience. Your client is training for a marathon. Here is the training week skeleton you created:
{training_week_skeleton}

Additionally, here is the weekly mileage target you provided:
{weekly_mileage_target}

Build out their next week of training. As a general rule, distribute volume and intensity evenly throughout the week as much as possible."""

    return get_completion_json(
        message=message,
        response_model=TrainingWeek,
    )


def generate_training_week(
    day_of_week_summaries: List[DayOfWeekSummary],
    weekly_summaries: List[WeekSummary],
):

    training_week_verbose = get_typical_training_week_verbose(day_of_week_summaries)
    training_week_skeleton = get_training_week_skeleton(training_week_verbose)
    weekly_mileage_target = get_weekly_mileage_target(weekly_summaries)
    training_week = get_training_week(training_week_skeleton, weekly_mileage_target)

    return training_week
