from pydantic import BaseModel


class DayOfWeekSummary(BaseModel):
    day_of_week: str
    number_of_runs: int
    avg_miles: float
    avg_pace: float

    def __str__(self):
        return f"{self.day_of_week}: {self.number_of_runs} runs, {self.avg_miles} miles, {self.avg_pace} min/mile"

    def __repr__(self):
        return str(self)
