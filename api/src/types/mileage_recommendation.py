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
