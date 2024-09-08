import sys

import numpy as np

sys.path.append("./")

import os

from src.auth_manager import get_strava_client
from src.email_manager import (
    new_training_week_to_html,
    send_email,
    training_week_update_to_html,
)
from src.supabase_client import get_user
from src.types.activity_summary import ActivitySummary
from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import (
    Day,
    Planning,
    SessionType,
    TrainingSession,
    TrainingWeekWithPlanning,
)

full_training_week = [
    TrainingSession(
        day=Day.MON,
        session_type=SessionType.EASY,
        distance=5.0,
        notes="Easy pace",
    ),
    TrainingSession(
        day=Day.TUES,
        session_type=SessionType.REST,
        distance=0.0,
        notes="No running, allowing muscles to recover and adapt",
    ),
    TrainingSession(
        day=Day.WED,
        session_type=SessionType.SPEED,
        distance=8.0,
        notes="2 miles warm-up, 3x1 mile @ 10k pace with 400m recovery jogs, 2 miles cooldown",
    ),
    TrainingSession(
        day=Day.THURS,
        session_type=SessionType.MODERATE,
        distance=6.0,
        notes="Moderate pace",
    ),
    TrainingSession(
        day=Day.FRI,
        session_type=SessionType.EASY,
        distance=5.0,
        notes="Easy pace",
    ),
    TrainingSession(
        day=Day.SAT,
        session_type=SessionType.LONG,
        distance=17.0,
        notes="Long run pace",
    ),
    TrainingSession(
        day=Day.SUN,
        session_type=SessionType.REST,
        distance=0.0,
        notes="Rest or very easy jogging recovery",
    ),
]

training_week_with_coaching = TrainingWeekWithCoaching(
    typical_week_training_review="Your current training schedule effectively incorporates long runs on Saturdays, which aligns well with your stated preference. Wednesdays appear to be ideal for your workouts as you log higher mileage with a pace of 9m 20s per mile, suggesting potential for speed work on this day. Your lighter runs and potential rest days could be on Sundays, allowing for recovery post long runs.",
    weekly_mileage_target="For the upcoming week, let's aim for a target weekly mileage of around 47 miles. Your longest run should range between 16 to 17 miles, ensuring a gradual increase without overexertion. Over recent weeks, you've successfully handled increasing mileage and can now focus on building endurance for your next marathon. Be attentive to your body's feedback, especially since you've had a consistent training routine.",
    planning="Planning(weekly_mileage_target=47 miles, long_run_distance=17.0, remaining_weekly_mileage=47 - 17 = 30 miles, remaining_weekly_mileage_planning=We have 30 miles left for the week after accounting for the long run of 17 miles. Here's a possible distribution: \n- Monday (Easy Run): 5 miles at an easy pace to start the week on a lighter note, helping with recovery from the weekend long run.\n- Tuesday (Rest Day): No running, allowing muscles to recover and adapt.\n- Wednesday (Speed Workout): 8 miles, including 2 miles warm-up, then 3x1 mile repeats at 10k pace with 400m recovery jogs, then 2 miles cooldown. This adds volume and builds speed endurance.\n- Thursday (Moderate Run): 6 miles at a steady, moderate pace to balance intensity and mileage.\n- Friday (Easy Run): 5 miles easy to keep the legs fresh for the long run.\n- Saturday (Long Run): 17 miles at a long run pace, focusing on endurance and sustaining a slow, steady effort.\n- Sunday (Rest Day): Complete rest or a very easy jogging recovery of choice for 1-2 miles at a conversational pace.)",
    training_week=full_training_week,
)


mid_week_analysis = MidWeekAnalysis(
    activities=[
        ActivitySummary(
            date="Monday, August 26, 2024",
            distance_in_miles=0.0,
            elevation_gain_in_feet=0.0,
            pace_minutes_per_mile=np.nan,
        ),
        ActivitySummary(
            date="Tuesday, August 27, 2024",
            distance_in_miles=10.04,
            elevation_gain_in_feet=213.25,
            pace_minutes_per_mile=9.56,
        ),
        ActivitySummary(
            date="Wednesday, August 28, 2024",
            distance_in_miles=10.01,
            elevation_gain_in_feet=390.42,
            pace_minutes_per_mile=9.24,
        ),
        ActivitySummary(
            date="Thursday, August 29, 2024",
            distance_in_miles=2.02,
            elevation_gain_in_feet=0.0,
            pace_minutes_per_mile=9.72,
        ),
        ActivitySummary(
            date="Friday, August 30, 2024",
            distance_in_miles=5.03,
            elevation_gain_in_feet=59.06,
            pace_minutes_per_mile=10.41,
        ),
    ],
    training_week=full_training_week,
)


training_week_update_with_planning = TrainingWeekWithPlanning(
    planning=Planning(
        weekly_mileage_target="47 miles",
        long_run_distance=17.0,
        remaining_weekly_mileage="30 miles",
        remaining_weekly_mileage_planning="We have 30 miles left ...",
    ),
    training_week=[
        TrainingSession(
            day=Day.SAT,
            session_type=SessionType.LONG,
            distance=16.0,
            notes="Long run at a conversational pace, around 9:20 min/mile",
        ),
        TrainingSession(
            day=Day.SUN,
            session_type=SessionType.EASY,
            distance=3.9,
            notes="Recovery run to aid in recovery after yesterday's long run",
        ),
    ],
)


def get_athlete_full_name(strava_client) -> str:
    athlete = strava_client.get_athlete()
    return f"{athlete.firstname} {athlete.lastname}"


def test_send_email():
    strava_client = get_strava_client(os.environ["JAMIES_ATHLETE_ID"])
    user = get_user(os.environ["JAMIES_ATHLETE_ID"])

    send_email(
        to={"email": user.email, "name": get_athlete_full_name(strava_client)},
        subject="Training Schedule Just Dropped 🏃‍♂️🎯",
        html_content=new_training_week_to_html(training_week_with_coaching),
    )

    send_email(
        to={"email": user.email, "name": get_athlete_full_name(strava_client)},
        subject="Training Schedule Update 🏃‍♂️🎯",
        html_content=training_week_update_to_html(
            mid_week_analysis=mid_week_analysis,
            training_week_update_with_planning=training_week_update_with_planning,
        ),
    )


test_send_email()
