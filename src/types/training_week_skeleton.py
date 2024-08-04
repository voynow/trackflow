from pydantic import BaseModel

from src.types.session_type import SessionType


class TrainingWeekSkeleton(BaseModel):
    mon: SessionType
    tues: SessionType
    wed: SessionType
    thurs: SessionType
    fri: SessionType
    sat: SessionType
    sun: SessionType

    def __str__(self):
        return "\n".join([f"{k}: {v}" for k, v in self.dict().items()])

    def __repr__(self):
        return self.__str__()
