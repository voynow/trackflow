from pydantic import BaseModel, Field

from src.types.session_type import SessionType


class TrainingSession(BaseModel):
    session_type: SessionType
    distance: float = Field(description="Distance in miles")
    notes: str = Field(description="notes for the session e.g. pace, terrain, etc.")

    def __str__(self):
        return f"{self.day}: {self.session_type}"

    def __repr__(self):
        return self.__str__()


class TrainingWeek(BaseModel):
    mon: TrainingSession
    tues: TrainingSession
    wed: TrainingSession
    thurs: TrainingSession
    fri: TrainingSession
    sat: TrainingSession
    sun: TrainingSession

    def __str__(self):
        return "\n".join(
            [
                f"{day}: {session['session_type']}, {session['distance']} miles, {session['notes']}"
                for day, session in self.dict().items()
            ]
        )

    def __repr__(self):
        return self.__str__()
