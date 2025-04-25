import datetime
from typing import Any

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

    The `0000-00-00` start date is supported by sending the `0000-00-00` flag in the context.
    For example:

    >>> IntervalPeriod.model_validate(data, context={"0000-00-00": datetime.datetime(2024, 9, 24)})
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

    @field_validator("start", mode="before")
    @classmethod
    def validate_start(cls, start: Any, info: ValidationInfo) -> Any:  # noqa: ANN401
        """Handle 0000-00-00 if configured."""
        if start == "0000-00-00" and info.context is not None and "0000-00-00" in info.context:
            return info.context["0000-00-00"]

        return start

    def __str__(self) -> str:
        """Return a description of the interval period."""
        return f"{self.start} - {self.start + self.duration} (± {self.randomize_start})"
