from typing import Optional

from pydantic import BaseModel


class FeedbackRow(BaseModel):
    """Represents a row in the feedback table"""

    feedback: str
    athlete_id: Optional[int]
    email: Optional[str]
    name: Optional[str]
