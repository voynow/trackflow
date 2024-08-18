from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.types.activity_summary import ActivitySummary
from src.types.training_week import TrainingSession


class MidWeekAnalysis(BaseModel):
    activities: list[ActivitySummary]
    training_week: List[TrainingSession]

    @property
    def training_week_future(self):
        return self.training_week[datetime.now().weekday() + 1 :]

    @property
    def miles_ran(self):
        return sum(activity.distance_in_miles for activity in self.activities)

    @property
    def miles_target(self):
        return sum(session.distance for session in self.training_week)

    @property
    def miles_remaining(self):
        return self.miles_target - self.miles_ran

    @property
    def future_miles_planned(self):
        return sum(session.distance for session in self.training_week_future)
