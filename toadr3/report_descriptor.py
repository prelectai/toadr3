from typing import Any

from .exceptions import SchemaException
from .values_map import parse_values_map


class ReportDescriptor:
    """An object that may be used to request a report from a VEN.

    See OpenADR REST User Guide for detailed description of how configure a report request.
    """

    def __init__(self, data: dict):
        if "payloadType" not in data:
            raise SchemaException("Missing 'payloadType' in report descriptor schema.")

        self._payload_type: str = data["payloadType"]
        self._reading_type: str | None = None
        self._units: str | None = None
        self._targets: dict[str, Any] | None = None
        self._aggregate: bool = False
        self._start_interval: int = -1
        self._num_intervals: int = -1
        self._historical: bool = True
        self._frequency: int = -1
        self._repeat: int = 1

        if "readingType" in data:
            self._reading_type = data["readingType"]

        if "units" in data:
            self._units = data["units"]

        if "targets" in data:
            self._targets = parse_values_map(data["targets"])

        if "aggregate" in data:
            self._aggregate = data["aggregate"]

        if "startInterval" in data:
            self._start_interval = int(data["startInterval"])

        if "numIntervals" in data:
            self._num_intervals = int(data["numIntervals"])

        if "historical" in data:
            self._historical = data["historical"]

        if "frequency" in data:
            self._frequency = int(data["frequency"])

        if "repeat" in data:
            self._repeat = int(data["repeat"])

    @property
    def payload_type(self) -> str:
        """The type of the payload."""
        return self._payload_type

    @property
    def reading_type(self) -> str | None:
        """The type of reading."""
        return self._reading_type

    @property
    def units(self) -> str | None:
        """The measurement units of the reading."""
        return self._units

    @property
    def targets(self) -> dict[str, Any] | None:
        """The targets of the report."""
        return self._targets

    @property
    def aggregate(self) -> bool:
        """Whether the report should be aggregated."""
        return self._aggregate

    @property
    def start_interval(self) -> int:
        """The interval at which to generate the report (-1 means end of last)."""
        return self._start_interval

    @property
    def num_intervals(self) -> int:
        """The number of intervals to include in the report."""
        return self._num_intervals

    @property
    def historical(self) -> bool:
        """Indicator for report data direction.

        True reports on intervals preceding startInterval,
        False reports on intervals following startInterval.
        """
        return self._historical

    @property
    def frequency(self) -> int:
        """Number of intervals between reports.

        -1 means the same as numIntervals.
        """
        return self._frequency

    @property
    def repeat(self) -> int:
        """The number of times to repeat the report.

        1 indicate generate one report, -1 indicate repeat indefinitely.
        """
        return self._repeat
