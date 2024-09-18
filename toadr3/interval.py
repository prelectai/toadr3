from typing import Any

from .exceptions import SchemaError
from .interval_period import IntervalPeriod
from .values_map import parse_values_map


class Interval:
    """Interval object.

    Has a payload for an IntervalPeriod. The IntervalPeriod is either local to the class or
    available from the parent Event object.
    """

    def __init__(self, data: dict):
        """Create an interval object from parsed JSON data."""
        self._data = data

        if "id" not in data:
            raise SchemaError("Missing 'id' in interval schema.")

        if "payloads" not in data:
            raise SchemaError("Missing 'payloads' in interval schema.")

        self._id = data["id"]
        self._interval_period = None
        self._payloads = parse_values_map(data["payloads"])

        if "intervalPeriod" in data:
            self._interval_period = IntervalPeriod(data["intervalPeriod"])

    @property
    def id(self) -> int:
        """The ID of the interval."""
        return self._data["id"]

    def has_interval_period(self) -> bool:
        """Check if the interval has an interval period."""
        return self._interval_period is not None

    @property
    def interval_period(self) -> IntervalPeriod | None:
        """The interval period of the interval."""
        return self._interval_period

    @property
    def payloads(self) -> dict[str, Any]:
        """The payloads of the interval."""
        return self._payloads
