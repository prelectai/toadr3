import datetime

from .exceptions import SchemaError
from .interval import Interval
from .interval_period import IntervalPeriod
from .payload_descriptor import PayloadDescriptor
from .report_descriptor import ReportDescriptor
from .values_map import parse_values_map


class Event:
    """Event object to communicate a Demand Response request to VEN.

    If intervalPeriod is present, sets start time and duration of intervals.
    """

    def __init__(self, data: dict):
        if "objectType" in data and data["objectType"] != "EVENT":
            raise SchemaError("Expected 'objectType' to be 'EVENT' in event schema.")

        if "programID" not in data:
            raise SchemaError("Missing 'programID' in event schema.")

        if "intervals" not in data:
            raise SchemaError("Missing 'intervals' in event schema.")

        self._id = data.get("id", None)
        self._program_id = data["programID"]
        self._intervals = [Interval(interval) for interval in data["intervals"]]
        self._name = data.get("eventName", None)
        self._interval_period = None
        self._created = None
        self._modified = None
        self._priority = None
        self._targets = None
        self._report_descriptors = None
        self._payload_descriptors = None

        if "intervalPeriod" in data:
            self._interval_period = IntervalPeriod(data["intervalPeriod"])

        if "createdDateTime" in data:
            self._created = datetime.datetime.fromisoformat(data["createdDateTime"])

        if "modificationDateTime" in data:
            self._modified = datetime.datetime.fromisoformat(data["modificationDateTime"])

        if "priority" in data:
            try:
                self._priority = int(data["priority"])
            except ValueError as err:
                msg = "Expected 'priority' to be an integer in event schema."
                raise SchemaError(msg) from err

        if "targets" in data:
            self._targets = parse_values_map(data["targets"])

        if "reportDescriptors" in data:
            self._report_descriptors = [
                ReportDescriptor(report) for report in data["reportDescriptors"]
            ]

        if "payloadDescriptors" in data:
            self._payload_descriptors = [
                PayloadDescriptor(payload) for payload in data["payloadDescriptors"]
            ]

    @property
    def id(self) -> str | None:
        """The ID of the event."""
        return self._id

    @property
    def event_name(self) -> str | None:
        """The name of the event."""
        return self._name

    @property
    def created(self) -> datetime.datetime | None:
        """The time the event was created."""
        return self._created

    @property
    def modified(self) -> datetime.datetime | None:
        """The time the event was last modified."""
        return self._modified

    @property
    def interval_period(self) -> IntervalPeriod | None:
        """Defines default start and durations of intervals."""
        return self._interval_period

    @property
    def intervals(self) -> list[Interval]:
        """List of interval objects."""
        return self._intervals

    @property
    def program_id(self) -> str:
        """The ID of the program object this event is associated with."""
        return self._program_id

    @property
    def priority(self) -> int | None:
        """The priority of the event."""
        return self._priority

    @property
    def targets(self) -> dict[str, list] | None:
        """The targets of the event."""
        return self._targets

    @property
    def report_descriptors(self) -> list[ReportDescriptor] | None:
        """The report descriptors of the event."""
        return self._report_descriptors

    @property
    def payload_descriptors(self) -> list[PayloadDescriptor] | None:
        """The payload descriptors of the event."""
        return self._payload_descriptors
