from pydantic import BaseModel

from src.types.training_week import TrainingWeek


class TrainingWeekWithCoaching(BaseModel):
    training_week: TrainingWeek
    """Client's recommended training week"""

    typical_week_training_review: str
    """Coach's review of the client's typical week of training"""

    weekly_mileage_target: str
    """Coach's prescribed weekly mileage target for the client"""
