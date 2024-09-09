from pydantic import BaseModel

from src.types.training_week import TrainingWeek
from src.utils import datetime_now_est


class MidWeekAnalysis(BaseModel):
    completed_training_week: TrainingWeek
    original_training_week: TrainingWeek

    @property
    def training_week_future(self):
        return TrainingWeek(
            sessions=self.original_training_week.sessions[
                datetime_now_est().weekday() + 1 :
            ]
        )

    @property
    def miles_ran(self):
        return self.completed_training_week.total_mileage

    @property
    def miles_target(self):
        return self.original_training_week.total_mileage

    @property
    def miles_remaining(self):
        return self.miles_target - self.miles_ran

    @property
    def future_miles_planned(self):
        return self.training_week_future.total_mileage
