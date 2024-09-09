import sys


sys.path.append("./")

import os
import datetime

from freezegun import freeze_time

from src.types.user_row import UserRow
from src.lambda_function import daily_executor
from src.supabase_client import get_user
from src.auth_manager import get_strava_client


def daily_executor_wrapper(date_str: str):

    day = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    print(f"E2E execution at {date_str} ({day})")

    @freeze_time(f"{date_str} 23:59:59")
    def test_daily_executor(user: UserRow):
        daily_executor(user)

    user = get_user(os.environ["JAMIES_ATHLETE_ID"])
    get_strava_client(user.athlete_id)
    return test_daily_executor(user)


# New training week
daily_executor_wrapper("2024-09-08")
 
# Update training week
daily_executor_wrapper("2024-09-09")
