import datetime

from .exceptions import SchemaError
from .iso_date import parse_iso8601_duration


class IntervalPeriod:
    """Interval period object.

    Represents a period of time with a start time, duration, and randomize start time.
    """

    def __init__(self, data: dict[str, str]):
        """Create an interval period object from parsed JSON data."""
        if "start" not in data:
            raise SchemaError("Missing 'start' in interval period schema.")

        self._start = datetime.datetime.fromisoformat(data["start"])
        self._duration = datetime.timedelta(seconds=0)
        self._randomize_start = datetime.timedelta(seconds=0)

        if "duration" in data:
            self._duration = parse_iso8601_duration(data["duration"])

        if "randomizeStart" in data:
            self._randomize_start = parse_iso8601_duration(data["randomizeStart"])

    @property
    def start(self) -> datetime.datetime:
        """The start of the interval period."""
        return self._start

    @property
    def duration(self) -> datetime.timedelta:
        """The duration of the interval period."""
        return self._duration

    @property
    def randomize_start(self) -> datetime.timedelta:
        """The randomize start of the interval period."""
        return self._randomize_start

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return (
            f"IntervalPeriod("
            f"start={self.start}, "
            f"duration={self.duration}, "
            f"randomize_start={self.randomize_start}"
            f")"
        )

    def __str__(self) -> str:
        """Return a description of the interval period."""
        return f"{self.start} - {self.start + self.duration} (± {self.randomize_start})"
