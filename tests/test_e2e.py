import os
import sys

from src.lambda_function import daily_executor
from src.supabase_client import get_user

sys.path.append("./")


import datetime

from freezegun import freeze_time


def daily_executor_wrapper(date_str: str):

    day = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    print(f"E2E execution at {date_str} ({day})")

    @freeze_time(f"{date_str} 23:59:59")
    def test_daily_executor():
        user = get_user(os.environ["JAMIES_ATHLETE_ID"])
        daily_executor(user)

    return test_daily_executor()


# New training week
daily_executor("2024-09-01")

# Update training week
daily_executor("2024-08-27")
