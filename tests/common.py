import os
from freezegun import freeze_time
from enum import Enum

from src.supabase_client import get_user
from src.email_manager import mock_send_email
from src.lambda_function import run_new_training_week_process, run_mid_week_update_process
from src.supabase_client import mock_upsert_training_week_update, mock_upsert_training_week_with_coaching
from src.supabase_client import list_users
from src.types.user_row import UserRow
from src.auth_manager import get_strava_client


def run_new_training_week_process_wrapped(
    mock_user: UserRow,
    date_str: str = "2024-08-25"
):
    @freeze_time(f"{date_str} 20:00:00")
    def run_new_training_week_process_freezed(mock_user: UserRow):
        return run_new_training_week_process(
            user=mock_user,
            upsert_fn=mock_upsert_training_week_with_coaching,
            email_fn=mock_send_email,
        )
    get_strava_client(mock_user.athlete_id)
    return run_new_training_week_process_freezed(mock_user)


def run_mid_week_update_process_wrapped(
    mock_user: UserRow, 
    date_str: str = "2024-08-27"
):

    @freeze_time(f"{date_str} 20:00:00")
    def run_mid_week_update_process_freezed(mock_user: UserRow):
        return run_mid_week_update_process(
            user=mock_user,
            upsert_fn=mock_upsert_training_week_update,
            email_fn=mock_send_email,
        )

    get_strava_client(mock_user.athlete_id)
    return run_mid_week_update_process_freezed(mock_user)