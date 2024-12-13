import logging
import os

import pytest
from src import auth_manager, supabase_client
from src.types.training_week import FullTrainingWeek
from src.types.update_pipeline import ExeType
from src.update_pipeline import _update_training_week
from src.utils import datetime_now_est, get_last_sunday

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    os.environ["TEST_FLAG"] = "true"
    auth_manager.authenticate_athlete(os.environ["JAMIES_ATHLETE_ID"])


def test_update_training_week_gen_mileage_recommendation():
    """
    gen_mileage_recommendation is called when the race date & distance are not set
    """
    user = supabase_client.get_user(os.environ["JAMIES_ATHLETE_ID"])
    user.preferences.race_date = None
    user.preferences.race_distance = None
    response = _update_training_week(user, ExeType.NEW_WEEK, dt=get_last_sunday())
    assert isinstance(response, FullTrainingWeek)


def test_update_training_week_gen_training_plan():
    """
    gen_training_plan_pipeline is called when the race date & distance are set
    """
    user = supabase_client.get_user(os.environ["JAMIES_ATHLETE_ID"])
    assert user.preferences.race_date is not None
    assert user.preferences.race_distance is not None
    response = _update_training_week(user, ExeType.NEW_WEEK, dt=get_last_sunday())
    assert isinstance(response, FullTrainingWeek)


def test_update_training_week_mid_week():
    """
    Test successful update of mid week

    This is the only mid week update path
    """
    user = supabase_client.get_user(os.environ["JAMIES_ATHLETE_ID"])
    response = _update_training_week(user, ExeType.MID_WEEK, dt=datetime_now_est())
    assert isinstance(response, FullTrainingWeek)
