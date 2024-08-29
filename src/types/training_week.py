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


class Planning(BaseModel):
    weekly_mileage_target: str = Field(
        description="String representation of the weekly mileage target"
    )
    long_run_distance: float = Field(
        description="The distance and day of the long run for the week"
    )
    remaining_weekly_mileage: str = Field(
        description="Write out the math (target - long run distance) to calculate the remaining weekly mileage"
    )
    remaining_weekly_mileage_planning: str = Field(
        description="Walk through, step by step, a practical distribution of the remaining weekly mileage across the week. Be very detailed, using math to ensure correctness on every step."
    )

    def __str__(self):
        return f"Planning(weekly_mileage_target={self.weekly_mileage_target}, long_run_distance={self.long_run_distance}, remaining_weekly_mileage={self.remaining_weekly_mileage}, remaining_weekly_mileage_planning={self.remaining_weekly_mileage_planning})"

    def __repr__(self):
        return self.__str__()


class TrainingWeekWithPlanning(BaseModel):
    planning: Planning
    training_week: List[TrainingSession] = Field(
        description="Unordered collection of REMAINING training sessions for the week"
    )

    @property
    def total_weekly_mileage(self) -> float:
        return sum(session.distance for session in self.training_week)

    def __str__(self):
        return f"TrainingWeekWithPlanning(planning={self.planning}, training_week={self.training_week})"

    def __repr__(self):
        return self.__str__()


class TrainingWeekWithCoaching(BaseModel):
    typical_week_training_review: str
    """Coach's review of the client's typical week of training"""

    weekly_mileage_target: str
    """Coach's prescribed weekly mileage target for the client"""

    planning: str
    """Internal planning for the client's training week"""

    training_week: List[TrainingSession]
    """Client's recommended training week"""

    @property
    def total_weekly_mileage(self) -> float:
        return sum(session.distance for session in self.training_week)

    def __str__(self):
        return f"TrainingWeekWithCoaching(typical_week_training_review={self.typical_week_training_review}, weekly_mileage_target={self.weekly_mileage_target}, planning={self.planning}, training_week={self.training_week})"

    def __repr__(self):
        return self.__str__()
