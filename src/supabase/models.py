import datetime

from pydantic import BaseModel


class UserAuthRow(BaseModel):
    id: NotImplementedError
    access_token: str
    refresh_token: str
    expires_at: datetime.datetime
