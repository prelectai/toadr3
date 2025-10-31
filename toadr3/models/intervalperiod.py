import datetime
from typing import Literal

from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo

from .docstringbasemodel import DocstringBaseModel
from .isoduration import parse_iso8601_duration


class IntervalPeriod(DocstringBaseModel):
    """Interval period object.

    Represents a period of time with a start time, duration, and randomize start time.

    P9999Y durations are supported by sending the `allow_P9999Y_duration` flag in the context.
    For example:

    >>> IntervalPeriod.model_validate(data, context={"allow_P9999Y_duration": True})

    The start field can also be set to the literal string "0000-00-00" to represent an
    unspecified start time. The __str__ method will interpret this as the current time.
    """

    # TODO @jepebe: if there is no time zone data, the Program object may have a timeZoneOffset
    #      that can be used to adjust the time to the correct timezone
    #      https://github.com/prelectai/toadr3/issues/23
    start: datetime.datetime | Literal["0000-00-00"]
    """The start of the interval period."""

    duration: datetime.timedelta = datetime.timedelta(seconds=0)
    """The duration of the interval period."""

    randomize_start: datetime.timedelta = datetime.timedelta(seconds=0)
    """The randomize start of the interval period."""

    @field_validator("duration", "randomize_start", mode="before")
    @classmethod
    def validate_timedeltas(
        cls, iso_duration: str | None, info: ValidationInfo
    ) -> datetime.timedelta:
        """Convert the iso duration to a timedelta object."""
        if iso_duration is None:
            return datetime.timedelta(seconds=0)

        if info.context is not None:
            allow = info.context.get("allow_P9999Y_duration", False)
            if allow and iso_duration == "P9999Y":
                return datetime.timedelta(days=365 * 9999)  # close enough

        return parse_iso8601_duration(iso_duration)

    def __str__(self) -> str:
        """Return a description of the interval period."""
        if isinstance(self.start, str):
            start = datetime.datetime.now(tz=datetime.UTC)
        else:
            start = self.start
        return f"{start} - {start + self.duration} (± {self.randomize_start})"
