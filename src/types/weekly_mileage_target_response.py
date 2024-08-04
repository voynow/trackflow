from pydantic import BaseModel, Field


class WeeklyMileageTargetResponse(BaseModel):
    thoughts: str = Field(
        description="Given your client's goals and training history, what should they work toward (# of miles per week) in the coming weeks? Walk through your thought process grounded in the numbers."
    )
    weekly_mileage_target: float = Field(
        description="How many miles should they run next week?"
    )

    def __str__(self):
        return f"Thoughts: {self.thoughts}\nWeekly Mileage Target: {self.weekly_mileage_target}"

    def __repr__(self):
        return self.__str__()
