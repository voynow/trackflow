from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel

from src.types.training_week import Day, SessionType


class RaceDistance(StrEnum):
    FIVE_KILOMETER = "5k"
    TEN_KILOMETER = "10k"
    HALF_MARATHON = "half marathon"
    MARATHON = "marathon"
    ULTRA = "ultra marathon"
    NONE = "none"


class TheoreticalTrainingSession(BaseModel):
    day: Day
    session_type: SessionType


class Preferences(BaseModel):
    race_distance: Optional[RaceDistance] = None
    ideal_training_week: Optional[List[TheoreticalTrainingSession]] = None


class UserRow(BaseModel):
    athlete_id: int
    preferences: str
    email: Optional[str] = None
    preferences_json: Optional[Preferences] = {}
    created_at: datetime = datetime.now()
