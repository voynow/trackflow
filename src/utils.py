from datetime import datetime

from zoneinfo import ZoneInfo


def datetime_now_est() -> datetime:
    """
    Returns the current time in the specified timezone

    :param zone: The timezone name (default is 'America/New_York')
    :return: The current datetime in the specified timezone
    """
    return datetime.now(ZoneInfo("America/New_York"))
