from typing import Any

from .exceptions import SchemaException
from .interval_period import IntervalPeriod
from .values_map import parse_values_map


class Interval:
    def __init__(self, data: dict):
        self._data = data

        if "id" not in data:
            raise SchemaException("Missing 'id' in interval schema.")

        if "payloads" not in data:
            raise SchemaException("Missing 'payloads' in interval schema.")

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
