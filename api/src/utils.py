from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pydantic import BaseModel


def datetime_now_est() -> datetime:
    """
    Returns the current time in the specified timezone

    :param zone: The timezone name (default is 'America/New_York')
    :return: The current datetime in the specified timezone
    """
    return datetime.now(ZoneInfo("America/New_York"))


def round_all_floats(model: BaseModel, precision: int = 2) -> BaseModel:
    """Round all float fields in a pydantic model to a given precision"""
    for field_name, field in model.__fields__.items():
        if (
            isinstance(field.type_, type)
            and issubclass(field.type_, float)
            and getattr(model, field_name) is not None
        ):
            setattr(model, field_name, round(getattr(model, field_name), precision))
    return model


def get_last_sunday():
    today = datetime_now_est().today()
    days_since_sunday = (today.weekday() + 1) % 7
    most_recent_sunday = today - timedelta(days=days_since_sunday)
    return most_recent_sunday.strftime("%Y-%m-%d")
