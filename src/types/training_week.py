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
        description="Walk through, step by step (with math), a practical distribution of the remaining weekly mileage across the week. Ex: Given 42 miles total - 17 mile long run = 25 miles remaining, lets distribute 25 miles over the remaining 6 days: One session of 10 miles (25 - 10 = 15 miles remaining). Two sessions of 6 miles (15 - 12 = 3 miles remaining). One sessions of 3 miles (3 - 3 = 0 miles remaining). Plus 2 rest days."
    )

    def __str__(self):
        return f"Planning(weekly_mileage_target={self.weekly_mileage_target}, long_run_distance={self.long_run_distance}, remaining_weekly_mileage={self.remaining_weekly_mileage}, remaining_weekly_mileage_planning={self.remaining_weekly_mileage_planning})"

    def __repr__(self):
        return self.__str__()


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


class TrainingWeekWithPlanning(BaseModel):
    planning: Planning
    training_week: TrainingWeek

    @property
    def total_weekly_mileage(self) -> float:
        return sum(session.distance for session in self.training_week)

    def __str__(self):
        return f"TrainingWeekWithPlanning(planning={self.planning}, training_week={self.training_week})"

    def __repr__(self):
        return self.__str__()


class TrainingWeekGeneration(BaseModel):
    """Specifically used for structured LLM generation"""

    weekly_mileage_target: float
    training_week: TrainingWeek
