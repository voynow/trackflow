from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserRow(BaseModel):
    athlete_id: int
    email: str
    preferences: str
    created_at: Optional[datetime] = None
