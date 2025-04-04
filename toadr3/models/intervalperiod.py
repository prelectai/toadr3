import datetime

from pydantic import field_validator

from .docstringbasemodel import DocstringBaseModel
from .isoduration import parse_iso8601_duration


class IntervalPeriod(DocstringBaseModel):
    """Interval period object.

    Represents a period of time with a start time, duration, and randomize start time.
    """

    # TODO @jepebe: if there is no time zone data, the Program object may have a timeZoneOffset
    #      that can be used to adjust the time to the correct timezone
    #      https://github.com/prelectai/toadr3/issues/23
    start: datetime.datetime
    """The start of the interval period."""

    duration: datetime.timedelta = datetime.timedelta(seconds=0)
    """The duration of the interval period."""

    randomize_start: datetime.timedelta = datetime.timedelta(seconds=0)
    """The randomize start of the interval period."""

    @field_validator("duration", "randomize_start", mode="before")
    @classmethod
    def validate_timedeltas(cls, iso_duration: str | None) -> datetime.timedelta:
        """Convert the iso duration to a timedelta object."""
        if iso_duration is None:
            return datetime.timedelta(seconds=0)
        return parse_iso8601_duration(iso_duration)

    def __str__(self) -> str:
        """Return a description of the interval period."""
        return f"{self.start} - {self.start + self.duration} (± {self.randomize_start})"
