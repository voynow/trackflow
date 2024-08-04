from pydantic import BaseModel


class WeekSummary(BaseModel):
    year: int
    week_of_year: int
    longest_run: float
    total_distance: float


    def __str__(self):
        return f"{self.year} - Week {self.week_of_year}: {self.total_distance} miles, longest run: {self.longest_run} miles"

    def __repr__(self):
        return str(self)
