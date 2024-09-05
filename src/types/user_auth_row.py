import datetime
from typing import Optional

from pydantic import BaseModel


class UserAuthRow(BaseModel):
    athlete_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime.datetime
    jwt_token: str
