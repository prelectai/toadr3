from .docstringbasemodel import DocstringBaseModel
from .intervalperiod import IntervalPeriod
from .valuesmap import ValuesMap


class Interval(DocstringBaseModel):
    """Interval object.

    Has a payload for an IntervalPeriod. The IntervalPeriod is either local to the class or
    available from the parent Event object.
    """

    id: int
    """The ID of the interval."""

    interval_period: IntervalPeriod | None = None
    """The interval period of the interval."""

    payloads: list[ValuesMap]
    """The payloads of the interval."""

    def has_interval_period(self) -> bool:
        """Check if the interval has an interval period."""
        return self.interval_period is not None
