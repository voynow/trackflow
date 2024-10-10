import sys

sys.path.append("./")

import datetime
import os

from freezegun import freeze_time

from src.auth_manager import get_strava_client
from src.supabase_client import get_user
from src.types.update_pipeline import ExeType
from src.types.user_row import UserRow
from src.update_pipeline import training_week_update_executor


def daily_executor_wrapper(date_str: str, exetype: ExeType):

    day = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    print(f"E2E execution at {date_str} ({day})")

    @freeze_time(f"{date_str} 23:59:59")
    def test_daily_executor(user: UserRow):
        training_week_update_executor(user, exetype)

    user = get_user(os.environ["JAMIES_ATHLETE_ID"])
    get_strava_client(user.athlete_id)
    return test_daily_executor(user)


# New training week
daily_executor_wrapper("2024-09-08", ExeType.NEW_WEEK)

# Update training week
daily_executor_wrapper("2024-09-09", ExeType.MID_WEEK)
