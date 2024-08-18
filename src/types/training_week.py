from enum import StrEnum
from typing import Dict, List

from pydantic import BaseModel, Field


class Day(StrEnum):
    MON = "mon"
    TUES = "tues"
    WED = "wed"
    THURS = "thurs"
    FRI = "fri"
    SAT = "sat"
    SUN = "sun"


class SessionType(StrEnum):
    EASY = "easy run"
    LONG = "long run"
    SPEED = "speed workout"
    REST = "rest day"
    MODERATE = "moderate run"


class TrainingSession(BaseModel):
    day: Day
    session_type: SessionType
    distance: float = Field(description="Distance in miles")
    notes: str = Field(
        description="Concise notes about the session, e.g. '2x2mi @ 10k pace' or 'easy pace'"
    )

    def __str__(self):
        return f"TrainingSession(session_type={self.session_type}, distance={self.distance}, weekly_mileage_cumulative={self.weekly_mileage_cumulative}, notes={self.notes})"


class TrainingWeekWithPlanning(BaseModel):
    planning: str = Field(
        description="Draft a plan (used internally) to aid in training week generation. You must adhere to the weekly mileage target and long run range. Do required math (step by step out loud) to plan the week successfully. If you end up exceeding the weekly mileage target, adjust one of the easy runs to be shorter."
    )
    training_week: List[TrainingSession] = Field(
        description="Unordered collection of training sessions for the week"
    )


class TrainingWeekWithCoaching(BaseModel):
    typical_week_training_review: str
    """Coach's review of the client's typical week of training"""

    weekly_mileage_target: str
    """Coach's prescribed weekly mileage target for the client"""

    training_week_planning: str
    """Internal planning for the client's training week"""

    training_week: List[TrainingSession]
    """Client's recommended training week"""

    @property
    def total_weekly_mileage(self) -> float:
        return sum(session.distance for session in self.training_week)

    def __str__(self):
        return f"{self.typical_week_training_review=}\n{self.weekly_mileage_target=}\n{self.training_week_planning=}\n{self.training_week=}"

    def __repr__(self):
        return self.__str__()
