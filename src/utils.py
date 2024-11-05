from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel
from zoneinfo import ZoneInfo


def datetime_now_est() -> datetime:
    """
    Returns the current time in the specified timezone

    :param zone: The timezone name (default is 'America/New_York')
    :return: The current datetime in the specified timezone
    """
    return datetime.now(ZoneInfo("America/New_York"))


def transpose_datamodel(models: List[BaseModel]) -> Dict[str, List[Any]]:
    return {
        field: [getattr(model, field) for model in models]
        for field in models[0].__fields__.keys()
    }
