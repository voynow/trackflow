import logging
import os
import traceback
from typing import Callable, Dict

import jwt

from src.activities import (
    get_activities_df,
    get_activity_summaries,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.auth_manager import authenticate_with_code, decode_jwt, get_strava_client
from src.constants import COACH_ROLE
from src.email_manager import (
    new_training_week_to_html,
    send_alert_email,
    send_email,
    training_week_update_to_html,
)
from src.new_training_week import generate_training_week_with_coaching
from src.supabase_client import (
    get_training_week_with_coaching,
    get_user,
    list_users,
    upsert_training_week_update,
    upsert_training_week_with_coaching,
    upsert_user,
)
from src.training_week_update import get_updated_training_week
from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import TrainingWeekWithCoaching, TrainingWeekWithPlanning
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


def handle_frontend_request(jwt_token: str):
    """
    To be extended for other requests eventually

    Validate JWT, then return training week with coaching
    """
    try:
        athlete_id = decode_jwt(jwt_token)
        training_week_with_coaching = get_training_week_with_coaching(athlete_id)
        return {
            "success": True,
            "training_week_with_coaching": training_week_with_coaching,
        }
    except jwt.DecodeError:
        return {"success": False, "error": "Invalid JWT token"}


def get_athlete_full_name(strava_client) -> str:
    athlete = strava_client.get_athlete()
    return f"{athlete.firstname} {athlete.lastname}"


def run_new_training_week_process(
    user: UserRow,
    upsert_fn: Callable[[str, TrainingWeekWithPlanning], None],
    email_fn: Callable[[Dict[str, str], str, str], None],
) -> TrainingWeekWithCoaching:
    """New training plan generation triggered weekly"""
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
    strava_client = get_strava_client(user.athlete_id)

    activities_df = get_activities_df(strava_client)
    day_of_week_summaries = get_day_of_week_summaries(activities_df)
    weekly_summaries = get_weekly_summaries(activities_df)
    training_week_with_coaching = generate_training_week_with_coaching(
        sysmsg_base=sysmsg_base,
        weekly_summaries=weekly_summaries,
        day_of_week_summaries=day_of_week_summaries,
    )

    upsert_fn(user.athlete_id, training_week_with_coaching)
    email_fn(
        to={"email": user.email, "name": get_athlete_full_name(strava_client)},
        subject="Training Schedule Just Dropped 🏃‍♂️🎯",
        html_content=new_training_week_to_html(training_week_with_coaching),
    )

    return training_week_with_coaching


def run_mid_week_update_process(
    user: UserRow,
    upsert_fn: Callable[[str, MidWeekAnalysis, TrainingWeekWithPlanning], None],
    email_fn: Callable[[Dict[str, str], str, str], None],
) -> TrainingWeekWithPlanning:
    """Mid-week training plan update triggered daily"""
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferences: {user.preferences}\n"
    strava_client = get_strava_client(user.athlete_id)

    training_week_with_coaching = get_training_week_with_coaching(user.athlete_id)
    current_weeks_activity_summaries = get_activity_summaries(
        strava_client, num_weeks=1
    )
    mid_week_analysis = MidWeekAnalysis(
        activities=current_weeks_activity_summaries,
        training_week=training_week_with_coaching.training_week,
    )
    training_week_update_with_planning = get_updated_training_week(
        sysmsg_base=sysmsg_base, mid_week_analysis=mid_week_analysis
    )

    upsert_fn(user.athlete_id, mid_week_analysis, training_week_update_with_planning)
    email_fn(
        to={"email": user.email, "name": get_athlete_full_name(strava_client)},
        subject="Training Schedule Update 🏃‍♂️🎯",
        html_content=training_week_update_to_html(
            mid_week_analysis=mid_week_analysis,
            training_week_update_with_planning=training_week_update_with_planning,
        ),
    )

    return training_week_update_with_planning


def daily_executor(user: UserRow) -> None:
    """
    On sundays, generate a new training week, otherwise update the current
    training week
    """
    try:
        # day 6 is Sunday
        if datetime_now_est().weekday() == 6:
            run_new_training_week_process(
                user=user,
                upsert_fn=upsert_training_week_with_coaching,
                email_fn=send_email,
            )
        else:
            run_mid_week_update_process(
                user=user,
                upsert_fn=upsert_training_week_update,
                email_fn=send_email,
            )
    except Exception as e:
        logging.error(f"Error processing user {user.athlete_id}: {e}")
        logging.error(traceback.format_exc())
        send_alert_email(
            subject="TrackFlow Alert: Error in Lambda Function",
            text_content=f"Error for {user.email=} {e} with traceback: {traceback.format_exc()}",
        )


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
    elif event.get("code"):
        user_auth = authenticate_with_code(event["code"])
        return {"success": True, "jwt_token": user_auth.jwt_token}

    elif event.get("jwt_token"):
        return handle_frontend_request(event["jwt_token"])

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
