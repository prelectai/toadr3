import datetime
import re


def parse_iso8601_duration(duration: str) -> datetime.timedelta:
    """Parse an ISO 8601 duration string into a timedelta object.

    Since Python's timedelta does not support years, months and weeks, this function will fail if
    those parts of the duration are specified. In addition, only seconds can have a fraction part.
    """
    pattern = (
        r"^P(?!$)"  # P is required to be at the start of the string
        r"(?:(?P<days>\d+)D)?"  # days are optional
        r"(?:T(?=\d)"  # T is required if time part is present
        r"(?:(?P<hours>\d+)H)?"  # hours are optional
        r"(?:(?P<minutes>\d+)M)?"  # minutes are optional
        r"(?:(?P<seconds>\d+\.\d+|\d*)S)?"  # seconds are optional (can be fractional)
        r")?$"  # end of string
    )
    match = re.match(pattern, duration)
    if not match:
        raise ValueError(f"Invalid ISO 8601 duration: {duration}")
    parts = {k: float(v) for k, v in match.groupdict("0").items()}
    return datetime.timedelta(**parts)
