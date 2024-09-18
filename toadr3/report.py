import datetime

from .exceptions import SchemaError
from .interval import Interval
from .interval_period import IntervalPeriod
from .payload_descriptor import PayloadDescriptor


class ReportData:
    """Report data for a resource."""

    def __init__(self, data: dict):
        """Create a new report data object from parsed JSON data.."""
        if "resourceName" not in data:
            raise SchemaError("Missing 'resourceName' in report data schema.")

        if "intervals" not in data:
            raise SchemaError("Missing 'intervals' in report data schema.")

        self._resource_name = data["resourceName"]
        self._intervals = [Interval(interval) for interval in data["intervals"]]
        self._interval_period = None

        if "intervalPeriod" in data:
            self._interval_period = IntervalPeriod(data["intervalPeriod"])

    @property
    def resource_name(self) -> str:
        """The name of the resource."""
        return self._resource_name

    @property
    def intervals(self) -> list[Interval]:
        """Applicable intervals for this report and resource."""
        return self._intervals

    @property
    def interval_period(self) -> IntervalPeriod | None:
        """The interval period for this report and resource (if available)."""
        return self._interval_period


class Report:
    """Report object for a report."""

    def __init__(self, data: dict):
        """Create a new report object from parsed JSON data."""
        if "objectType" in data and data["objectType"] != "REPORT":
            raise SchemaError("Expected 'objectType' to be 'REPORT' in report data schema.")

        if "programID" not in data:
            raise SchemaError("Missing 'programID' in report schema.")

        if "eventID" not in data:
            raise SchemaError("Missing 'eventID' in report schema.")

        if "clientName" not in data:
            raise SchemaError("Missing 'clientName' in report schema.")

        if "resources" not in data:
            raise SchemaError("Missing 'resources' in report schema.")

        self._id = data.get("id", None)
        self._created = None
        self._modified = None
        self._program_id = data["programID"]
        self._event_id = data["eventID"]
        self._client_name = data["clientName"]
        self._report_name = data.get("reportName", None)
        self._payload_descriptors = None
        self._resources = [ReportData(resource) for resource in data["resources"]]

        if "createdDateTime" in data:
            self._created = datetime.datetime.fromisoformat(data["createdDateTime"])

        if "modificationDateTime" in data:
            self._modified = datetime.datetime.fromisoformat(data["modificationDateTime"])

        if "payloadDescriptors" in data:
            self._payload_descriptors = [
                PayloadDescriptor(payload) for payload in data["payloadDescriptors"]
            ]

    @property
    def id(self) -> str | None:
        """The ID of the report."""
        return self._id

    @property
    def created(self) -> datetime.datetime | None:
        """The creation date of the report."""
        return self._created

    @property
    def modified(self) -> datetime.datetime | None:
        """The modification date of the report."""
        return self._modified

    @property
    def program_id(self) -> str:
        """The program ID of the report."""
        return self._program_id

    @property
    def event_id(self) -> str:
        """The event ID of the report."""
        return self._event_id

    @property
    def client_name(self) -> str:
        """The client name of the report."""
        return self._client_name

    @property
    def report_name(self) -> str | None:
        """The name of the report."""
        return self._report_name

    @property
    def payload_descriptors(self) -> list[PayloadDescriptor] | None:
        """The payload descriptors of the report."""
        return self._payload_descriptors

    @property
    def resources(self) -> list[ReportData]:
        """The resources of the report."""
        return self._resources
