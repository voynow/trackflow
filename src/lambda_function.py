import os

from src.activities import (
    get_activities_df,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.auth_manager import get_strava_client
from src.constants import COACH_ROLE
from src.email_manager import send_email, training_week_to_html
from src.supabase_client import upsert_training_week_with_coaching
from src.training_week import generate_training_week


def lambda_handler(event, context):
    client_preferences = "A) Training for a marathon B) This will be my second marathon C) Prefer workouts on Wednesdays and long runs on Saturdays"
    sysmsg_base = f"{COACH_ROLE}\nYour client has included the following preferenced: {client_preferences}\n"
    # activities setup
    athlete_id = os.environ["JAMIES_ATHLETE_ID"]
    strava_client = get_strava_client(athlete_id)
    activities_df = get_activities_df(strava_client)

    # gen training week pipeline
    day_of_week_summaries = get_day_of_week_summaries(activities_df)
    weekly_summaries = get_weekly_summaries(activities_df)
    training_week_with_coaching = generate_training_week(
        sysmsg_base=sysmsg_base,
        weekly_summaries=weekly_summaries,
        day_of_week_summaries=day_of_week_summaries,
    )

    # save data to db and trigger email
    upsert_training_week_with_coaching(
        athlete_id=athlete_id, training_week_with_coaching=training_week_with_coaching
    )
    send_email(
        subject="Training Schedule Just Dropped 🏃",
        html_content=training_week_to_html(training_week_with_coaching),
    )
