from pydantic import BaseModel


class ActivitySummary(BaseModel):
    date_and_time: str
    """Datetime formatted as 'Monday, August 13, 2024 08:00 PM'"""

    distance_in_miles: float
    elevation_gain_in_feet: float
    pace_minutes_per_mile: float
