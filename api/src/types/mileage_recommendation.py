import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MileageRecommendation(BaseModel):
    thoughts: str = Field(
        description="Given the past week's training, where is your athlete trending in terms of volume?"
    )
    total_volume: int = Field(
        description="How many miles should your athlete aim for in the next week?"
    )
    long_run: int = Field(
        description="How many miles should your athlete aim for in their long run in the next week?"
    )


class MileageRecommendationRow(BaseModel):
    """Database row representation of mileage_recommendation table"""

    week_of_year: Optional[int]
    year: Optional[int]
    thoughts: Optional[str]
    total_volume: Optional[int]
    long_run: Optional[int]
    athlete_id: Optional[int]
    created_at: datetime.datetime = datetime.datetime.now()

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        if isinstance(data["created_at"], datetime.datetime):
            data["created_at"] = data["created_at"].isoformat()
        return data
