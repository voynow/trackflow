from pydantic import BaseModel


class StravaEvent(BaseModel):
    subscription_id: int
    aspect_type: str
    object_type: str
    object_id: int
    owner_id: int
