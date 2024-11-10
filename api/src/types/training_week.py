from __future__ import annotations

from enum import StrEnum
from typing import List

from pydantic import BaseModel, Field


class Day(StrEnum):
    MON = "Mon"
    TUES = "Tues"
    WED = "Wed"
    THURS = "Thurs"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"


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
        description="Detailed yet concise notes about the session from the coach's perspective"
    )
    completed: bool = Field(description="Whether the session has been completed")


class TrainingWeek(BaseModel):
    sessions: List[TrainingSession]

    @property
    def total_mileage(self) -> float:
        return sum(session.distance for session in self.sessions)

    @property
    def progress(self) -> float:
        return (self.completed_sessions.total_mileage / self.total_mileage) * 100

    @property
    def completed_sessions(self) -> TrainingWeek:
        return TrainingWeek(
            sessions=[session for session in self.sessions if session.completed is True]
        )
