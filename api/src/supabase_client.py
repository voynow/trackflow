from __future__ import annotations

import json
import os
from enum import StrEnum
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from supabase import Client, create_client

load_dotenv()


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


def init() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)


client = init()


def get_training_week(athlete_id: int) -> TrainingWeek:
    """
    Get the most recent training_week row by athlete_id.
    """
    table = client.table("training_week")
    response = (
        table.select("training_week")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    try:
        response_data = response.data[0]
        return TrainingWeek(**json.loads(response_data["training_week"]))
    except IndexError:
        raise ValueError(
            f"Could not find training_week row for athlete_id {athlete_id}"
        )
