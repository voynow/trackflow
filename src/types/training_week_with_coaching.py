from pydantic import BaseModel

from src.types.training_week import TrainingWeek


class TrainingWeekWithCoaching(BaseModel):
    training_week: TrainingWeek
    """Client's recommended training week"""

    typical_week_training_review: str
    """Coach's review of the client's typical week of training"""

    weekly_mileage_target: str
    """Coach's prescribed weekly mileage target for the client"""

    def __str__(self):
        return f"{self.training_week}\n\ntypical_week_training_review: {self.typical_week_training_review}\nweekly_mileage_target: {self.weekly_mileage_target}"

    def __repr__(self):
        return self.__str__()
