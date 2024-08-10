import os

from src.activities import (
    get_activities_df,
    get_day_of_week_summaries,
    get_weekly_summaries,
)
from src.auth_manager import get_strava_client
from src.email_manager import send_email, training_week_to_html
from src.supabase_client import upsert_training_week_with_coaching
from src.training_week import generate_training_week


def lambda_handler(event, context):

    athlete_id = os.environ["JAMIES_ATHLETE_ID"]
    strava_client = get_strava_client(athlete_id)

    # process activities data
    activities_df = get_activities_df(strava_client)
    day_of_week_summaries = get_day_of_week_summaries(activities_df)
    weekly_summaries = get_weekly_summaries(activities_df)

    # Generate the training week
    training_week = generate_training_week(weekly_summaries, day_of_week_summaries)
    upsert_training_week_with_coaching(
        athlete_id=athlete_id, training_week_with_coaching=training_week
    )

    send_email(
        subject="Training Schedule Just Dropped 🏃",
        html_content=training_week_to_html(training_week),
    )
