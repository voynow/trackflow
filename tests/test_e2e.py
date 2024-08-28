import sys

sys.path.append("./")


import datetime

from freezegun import freeze_time

from src import lambda_function


def lambda_handler_freeze_wrapper(date_str: str):

    day = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
    print(f"E2E execution at {date_str} ({day})")

    @freeze_time(f"{date_str} 20:00:00")
    def test_lambda_handler():
        lambda_function.lambda_handler({"end_to_end_test": True}, None)

    return test_lambda_handler()


# New training week
lambda_handler_freeze_wrapper("2024-08-25")

# Update training week
lambda_handler_freeze_wrapper("2024-08-27")
