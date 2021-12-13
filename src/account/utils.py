from datetime import datetime, timedelta
import pytz
from typing import Union


def get_server_time(user_time: str) -> Union[str, None]:
    """Get server alert time from user input.
    Takes user time, calculates shift relative to UTC and returns timezone

    Args:
        user_time: string gotten from user.

    Returns:
        Timezone name in format, for example Asia/Omsk.
    """
    hour, minute = [int(i) for i in user_time.split(':')]
    now = datetime.now(pytz.utc)
    user_time = now.replace(hour=hour, minute=minute)

    delta_hours = round((user_time - now).total_seconds() // 3600)
    # getting timezones of xx:30 format: first converting seconds, to minutes, then removing excess hours
    # and then counting, how much half-hours passed
    delta_minutes = round((user_time - now).total_seconds() // 60 % 60 // 30)
    delta_time = timedelta(hours=delta_hours, minutes=delta_minutes * 30)


    for tz in map(pytz.timezone, pytz.all_timezones_set):
        dt = now.astimezone(tz)
        tzinfos = getattr(tz, '_tzinfos',
                          [(dt.utcoffset(), dt.dst(), dt.tzname())])
        if any(off == delta_time for off, _, _ in tzinfos):
            return tz.zone

    return None
