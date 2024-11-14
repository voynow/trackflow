from pydantic import BaseModel


class StravaEvent(BaseModel):
    """
    Strava webhook event
    """
    subscription_id: int
    aspect_type: str
    object_type: str
    object_id: int
    owner_id: int
    event_time: int
    updates: dict
