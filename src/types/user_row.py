from datetime import datetime

from pydantic import BaseModel


class UserRow(BaseModel):
    athlete_id: int
    email: str
    preferences: str
    created_at: datetime
