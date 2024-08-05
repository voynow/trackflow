from enum import StrEnum

class SessionType(StrEnum):
    EASY = "easy run"
    LONG = "long run"
    SPEED = "speed workout"
    REST = "rest day"
    MODERATE = "moderate run"
    