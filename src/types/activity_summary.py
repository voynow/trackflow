from pydantic import BaseModel


class ActivitySummary(BaseModel):
    date: str
    """Datetime formatted as 'Monday, August 13, 2024'"""

    distance_in_miles: float
    elevation_gain_in_feet: float
    pace_minutes_per_mile: float
