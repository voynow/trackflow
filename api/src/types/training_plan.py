from datetime import date
from typing import List

from pydantic import BaseModel, Field
from strenum import StrEnum


class WeekRange(BaseModel):
    start_date: date
    end_date: date
    week_number: int
    n_weeks_until_race: int

    def __str__(self):
        return f"WeekRange(week_number={self.week_number}, n_weeks_until_race={self.n_weeks_until_race}, start_date={self.start_date}, end_date={self.end_date})"


class WeekType(StrEnum):
    BUILD = "build"
    PEAK = "peak"
    TAPER = "taper"
    RACE = "race"


class TrainingPlanWeek(BaseModel):
    week_start_date: date
    week_number: int
    n_weeks_until_race: int
    week_type: WeekType
    notes: str = Field(
        description="How will this week contribute to the athlete's goal of running race_distance miles by the race_date?"
    )
    total_distance: float = Field(
        description="How many miles the athlete should aim to run in this week"
    )
    long_run_distance: float = Field(
        description="How many miles the athlete should aim to run in their long run this week"
    )


class TrainingPlan(BaseModel):
    training_week_plans: List[TrainingPlanWeek]


class TrainingPlanWeekRow(BaseModel):
    athlete_id: int
    week_start_date: date
    week_number: int
    n_weeks_until_race: int
    week_type: WeekType
    notes: str
    total_distance: float
    long_run_distance: float
