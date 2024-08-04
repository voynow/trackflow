from enum import StrEnum

from pydantic import BaseModel


class DayOfWeek(StrEnum):
    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"


days_of_week_order = [
    DayOfWeek.MON,
    DayOfWeek.TUE,
    DayOfWeek.WED,
    DayOfWeek.THU,
    DayOfWeek.FRI,
    DayOfWeek.SAT,
    DayOfWeek.SUN,
]


class DayOfWeekSummary(BaseModel):
    day_of_week: DayOfWeek
    number_of_runs: int
    avg_miles: float
    avg_pace: float


    def __str__(self):
        return f"{self.day_of_week}: {self.number_of_runs} runs, {self.avg_miles} miles, {self.avg_pace} min/mile"
