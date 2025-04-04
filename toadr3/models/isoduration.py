import datetime
import re


def parse_iso8601_duration(duration: str) -> datetime.timedelta:
    """Parse an ISO 8601 duration string into a timedelta object.

    Since Python's timedelta does not support years, months and weeks, this function will fail if
    those parts of the duration are specified. In addition, only seconds can have a fraction part.

    We have added support for weeks by adding 7 days to the days part of the timedelta.

    Months and years are not supported because they have variable lengths and are not suitable for
    conversion to a fixed number of days without a reference date.
    """
    dec_or_int = r"((\d+[.]\d+)|(\d+))"  # decimal or integer
    pattern = (
        r"^(?:(?P<negative>[-]?))?"  # negative sign is optionally at the start of the string
        r"P(?!$)"  # P is required to be at the start of the string
        r"(?:(?P<weeks>[-]?\d+)W)?"  # weeks are optional
        r"(?:(?P<days>[-]?\d+)D)?"  # days are optional
        rf"(?:T(?=[-]?{dec_or_int}[HMS])"  # T is required if time part is present (+ look ahead)
        r"(?:(?P<hours>[-]?\d+)H)?"  # hours are optional
        r"(?:(?P<minutes>[-]?\d+)M)?"  # minutes are optional
        rf"(?:(?P<seconds>[-]?{dec_or_int})S)?"  # seconds are optional (can be fractional)
        r")?$"  # end of string
    )
    match = re.match(pattern, duration)
    if not match:
        raise ValueError(f"Invalid ISO 8601 duration: {duration}")

    factor = 1
    parts = {}
    for k, v in match.groupdict("0").items():
        if k == "negative":
            if v == "-":
                factor = -1
        else:
            parts[k] = float(v) * factor

    if "weeks" in parts:
        if "days" not in parts:
            parts["days"] = 0
        parts["days"] += parts.pop("weeks") * 7

    return datetime.timedelta(**parts)


def create_iso8601_duration(delta: datetime.timedelta) -> str:
    """Create an ISO 8601 duration string from a timedelta object.

    If the timedelta is negative, the duration will be prefixed with a negative sign.

    Parameters
    ----------
    delta : datetime.timedelta
        The timedelta object to convert to an ISO 8601 duration string.

    Returns
    -------
    str
        The ISO 8601 duration string.
    """
    seconds = delta.total_seconds()

    if seconds == 0:
        return "PT0S"

    negative = ""
    if seconds < 0:
        negative = "-"
        seconds = abs(seconds)

    weeks, seconds = divmod(seconds, 7 * 24 * 3600)
    days, seconds = divmod(seconds, 24 * 3600)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    duration = f"{negative}P"
    if weeks != 0:
        duration += f"{int(weeks)}W"

    if days != 0:
        duration += f"{int(days)}D"

    if hours != 0 or minutes != 0 or seconds != 0:
        duration += "T"

    if hours != 0:
        duration += f"{int(hours)}H"

    if minutes != 0:
        duration += f"{int(minutes)}M"

    if seconds != 0:
        if seconds.is_integer():
            duration += f"{int(seconds)}S"
        else:
            num = f"{seconds:f}".rstrip("0").rstrip(".")
            duration += f"{num}S"
    return duration
