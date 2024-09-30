import datetime
from typing import Any

from .event import Event
from .exceptions import SchemaError
from .interval import Interval
from .interval_period import IntervalPeriod
from .report_payload_descriptor import ReportPayloadDescriptor


class ReportData:
    """Report data for a resource."""

    def __init__(self, data: dict):
        """Create a new report data object from parsed JSON data."""
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
                ReportPayloadDescriptor(payload) for payload in data["payloadDescriptors"]
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
    def payload_descriptors(self) -> list[ReportPayloadDescriptor] | None:
        """The payload descriptors of the report."""
        return self._payload_descriptors

    @property
    def resources(self) -> list[ReportData]:
        """The resources of the report."""
        return self._resources


def create_report(
    event: Event,
    client_name: str,
    report_type: str,
    report_values: list[Any],
    report_name: str | None = None,
) -> Report:
    """Create a new report object.

    This will create a single report object for the given event for the specific report types.
    There are several assumptions made in this function:
    1. You want/can only create a report for one report descriptor (at a time).
    2. There is only one target the report applies to.
    3. There is only one interval, and it is specified in an 'intervalPeriod' at the root level.

    Parameters
    ----------
    event : Event
        The event object to create the report for.
    client_name : str
        The client name for the report.
    report_type : str
        The report type for the report (payload type of one of report descriptors).
    report_values : list[Any]
        The report values for the report.
    report_name : str, optional
        The name for the report (for debugging).

    Raises
    ------
    ValueError
        For missing and invalid arguments.

    Returns
    -------
    Report
        The created report object.
    """
    if not client_name or not isinstance(client_name, str):
        raise ValueError("client_name is required.")

    if not report_type or not isinstance(report_type, str):
        raise ValueError("report_type is required.")

    if not report_values or not isinstance(report_values, list):
        raise ValueError("report_values is required.")

    if event.program_id is None:
        raise ValueError("event must have a program ID.")

    if event.id is None:
        raise ValueError("event must have an ID.")

    if event.interval_period is None:
        raise ValueError("event must have an interval period.")

    if "RESOURCE_NAME" not in event.targets:
        raise ValueError("event does not have a target for RESOURCE_NAME.")

    data = {
        "objectType": "REPORT",
        "programID": event.program_id,
        "eventID": event.id,
        "clientName": client_name,
    }

    if report_name is not None:
        data["reportName"] = report_name

    if event.report_descriptors is None or len(event.report_descriptors) == 0:
        raise ValueError("event does not have any report_descriptors.")

    report_descriptor = None
    for rd in event.report_descriptors:
        if rd.payload_type == report_type:
            report_descriptor = rd
            break

    if report_descriptor is None:
        raise ValueError(f"event does not have a report_descriptor for {report_type}.")

    data["payloadDescriptors"] = [{"payloadType": report_type}]

    data["resources"] = [
        {
            "resourceName": event.targets["RESOURCE_NAME"][0],
            "intervalPeriod": _parse_interval_period(event.interval_period),
            "intervals": [
                {
                    "id": 0,
                    "payloads": [
                        {
                            "type": report_type,
                            "values": report_values,
                        }
                    ],
                }
            ],
        }
    ]

    return Report(data)


def _parse_interval_period(interval_period: IntervalPeriod) -> dict[str, Any]:
    """Convert the interval period to a JSON encodable python dict.

    This uses the ToadrJSONEncoder to convert the IntervalPeriod object to a dict,
    since the encoder functions returns dicts with JSON encodable types.
    """
    from .serializer import ToadrJSONEncoder  # imported here to avoid circular import

    encoder = ToadrJSONEncoder()
    return encoder.serialize_interval_period(interval_period)
