from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel

from src.types.training_week import Day


class RaceDistance(StrEnum):
    FIVE_KILOMETER = "5k"
    TEN_KILOMETER = "10k"
    HALF_MARATHON = "half marathon"
    MARATHON = "marathon"
    ULTRA = "ultra marathon"


class Preferences(BaseModel):
    race_distance: Optional[RaceDistance] = None
    long_run_day: Optional[Day] = None
    speed_workout_day: Optional[Day] = None
    n_days_per_week: Optional[int] = None
    unavailable_days: Optional[List[Day]] = None


class UserRow(BaseModel):
    athlete_id: int
    email: str
    preferences: str
    preferences_json: Preferences = {}
    is_active: bool = True
    created_at: datetime = datetime.now()
