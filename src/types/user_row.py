from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserRow(BaseModel):
    athlete_id: int
    email: str
    preferences: str
    is_active: bool = True
    created_at: datetime = datetime.now()
