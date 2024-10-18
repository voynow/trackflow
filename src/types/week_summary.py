from datetime import datetime

from pydantic import BaseModel


class WeekSummary(BaseModel):
    year: int
    week_of_year: int
    week_start_date: datetime
    longest_run: float
    total_distance: float

    def __str__(self):
        return f"WeekSummary(year={self.year}, week_of_year={self.week_of_year}, week_start_date={self.week_start_date}, longest_run={self.longest_run}, total_distance={self.total_distance})"

    def __repr__(self):
        return str(self)
