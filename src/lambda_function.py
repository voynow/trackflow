import logging
import os
import traceback
from typing import Callable, Optional

from stravalib.client import Client

from src.activities import (
    get_activities_df,
    get_activity_summaries,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.auth_manager import authenticate_with_code, get_strava_client
from src.constants import COACH_ROLE
from src.email_manager import (
    send_alert_email,
    send_email,
    training_week_to_html,
)
from src.mid_week_update import generate_mid_week_update
from src.new_training_week import generate_new_training_week
from src.supabase_client import (
    get_training_week,
    get_user,
    list_users,
    upsert_training_week,
    upsert_user,
)
from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import TrainingWeek
from src.types.user_row import UserRow
from src.utils import datetime_now_est


def signup(email: str, preferences: str, code: str) -> str:
    """
    Get authenticated user, upsert user with email and preferences

    :param email: user email
    :param preferences: user preferences
    :param code: strava code
    :return: jwt_token
    """
    send_alert_email(
        subject="TrackFlow Alert: New Signup Attempt",
        text_content=f"You have a new client {email=} attempting to signup with {preferences=}",
    )
    user_auth = authenticate_with_code(code)
    upsert_user(
        UserRow(
            athlete_id=user_auth.athlete_id,
            email=email,
            preferences=preferences,
        )
    )
    return user_auth.jwt_token


def new_training_week_pipeline(
    user: UserRow,
    strava_client: Client,
) -> TrainingWeek:
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
    activities_df = get_activities_df(strava_client)
    day_of_week_summaries = get_day_of_week_summaries(activities_df)
    weekly_summaries = get_weekly_summaries(activities_df)
    return generate_new_training_week(
        sysmsg_base=sysmsg_base,
        weekly_summaries=weekly_summaries,
        day_of_week_summaries=day_of_week_summaries,
    )


def mid_week_update_pipeline(
    user: UserRow,
    strava_client: Client,
) -> TrainingWeek:
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
    training_week = get_training_week(user.athlete_id)
    completed_activities = get_activity_summaries(strava_client, num_weeks=1)
    return generate_mid_week_update(
        sysmsg_base=sysmsg_base,
        training_week=training_week,
        completed_activities=completed_activities,
    )


def daily_generic_pipeline(
    user: UserRow,
    pipeline_function: Callable[[UserRow, Client], TrainingWeek],
    email_subject: str,
) -> TrainingWeek:
    """General processing for training week updates."""
    strava_client = get_strava_client(user.athlete_id)
    athlete = strava_client.get_athlete()
    training_week = pipeline_function(user=user, strava_client=strava_client)

    upsert_training_week(user.athlete_id, training_week)
    send_email(
        to={"email": user.email, "name": f"{athlete.firstname} {athlete.lastname}"},
        subject=email_subject,
        html_content=training_week_to_html(training_week),
    )
    return training_week


def daily_executor(user: UserRow) -> Optional[TrainingWeek]:
    """Decides between generating a new week or updating based on the day."""
    try:
        # Sunday is day 6
        if datetime_now_est().weekday() == 6:
            return daily_generic_pipeline(
                user=user,
                pipeline_function=new_training_week_pipeline,
                email_subject="Training Schedule Just Dropped 🏃‍♂️🎯",
            )
        else:
            return daily_generic_pipeline(
                user=user,
                pipeline_function=mid_week_update_pipeline,
                email_subject="Training Schedule Update 🏃‍♂️🎯",
            )
    except Exception as e:
        logging.error(f"Error processing user {user.athlete_id}: {e}")
        send_alert_email(
            subject="TrackFlow Alert: Error in Lambda Function",
            text_content=f"Error for {user.email=} {e} with traceback: {traceback.format_exc()}",
        )
        return None


def lambda_handler(event, context):
    """
    Main entry point for production workload. For simplicity, I've designed this
    lambda to act like an API of sorts, using if/else logic to route events to
    the correct function.

    :param event: lambda event
    :param context: lambda context
    :return: dict with {"success": bool}
    """
    print(f"Event: {event}")
    print(f"Context: {context}")

    # Will fail on bad authenticate_with_code
    if event.get("email") and event.get("preferences") and event.get("code"):
        response = signup(
            email=event["email"],
            preferences=event["preferences"],
            code=event["code"],
        )
        return {"success": True, "jwt_token": response}

    # Will fail on bad authenticate_with_code
    if event.get("code"):
        user_auth = authenticate_with_code(event["code"])
        return {"success": True, "jwt_token": user_auth.jwt_token}

    # This will only run if triggered by NIGHTLY_EMAIL_TRIGGER_ARN
    elif (
        event.get("resources")
        and event.get("resources")[0] == os.environ["NIGHTLY_EMAIL_TRIGGER_ARN"]
    ):
        [daily_executor(user) for user in list_users()]
        return {"success": True}

    # Will email me only
    elif event.get("end_to_end_test"):
        user = get_user(os.environ["JAMIES_ATHLETE_ID"])
        daily_executor(user)
        return {"success": True}

    # Catch any error routing or funny business
    else:
        send_alert_email(
            subject="TrackFlow Alert: Unknown Lambda Invocation",
            text_content=f"Unknown invocation of lambda with {event=} and {context=}",
        )
        return {"success": False}
