import sys

sys.path.append(".")

import os
from unittest.mock import ANY, patch

import pytest

from src.supabase_client import get_user
from src.types.update_pipeline import ExeType
from src.update_pipeline import update_training_week

USER = get_user(os.environ["JAMIES_ATHLETE_ID"])


@pytest.mark.parametrize("exe_type", [ExeType.NEW_WEEK, ExeType.MID_WEEK])
def test_update_training_week(exe_type):
    with patch("src.update_pipeline.upsert_training_week") as mock_upsert, patch(
        "src.update_pipeline.send_push_notif_wrapper"
    ) as mock_send_push:

        result = update_training_week(USER, exe_type)
        assert result == {"success": True}
        mock_upsert.assert_called_with(USER.athlete_id, ANY)
        mock_send_push.assert_called_once_with(USER)
