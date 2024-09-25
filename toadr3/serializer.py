import datetime
import json
from typing import Any

from .event import Event
from .event_payload_descriptor import EventPayloadDescriptor
from .interval import Interval
from .interval_period import IntervalPeriod
from .iso_date import create_iso8601_duration
from .report import Report, ReportData
from .report_descriptor import ReportDescriptor
from .report_payload_descriptor import ReportPayloadDescriptor


def _serialize_values_map(values_map: dict[str, list[str, Any]]) -> list[dict[str, Any]]:
    """Serialize a values map to a JSON compatible object."""
    result = []
    for key, values in values_map.items():
        result.append({"type": key, "values": values})
    return result


class ToadrJSONEncoder(json.JSONEncoder):
    """JSON encoder for objects in the toadr3 library."""

    def default(self, obj: object) -> object:
        """Serialize objects in the toadr3 library to JSON.

        All objects that are part of the toadr3 library are supported here,
        including datetime objects and timedelta objects.
        """
        # the following match/case uses the class pattern matching feature
        match obj:
            case datetime.datetime():
                result = obj.isoformat()
            case datetime.timedelta():
                result = create_iso8601_duration(obj)
            case IntervalPeriod():
                result = self.serialize_interval_period(obj)
            case Interval():
                result = self.serialize_interval(obj)
            case ReportData():
                result = self.serialize_report_data(obj)
            case Report():
                result = self.serialize_report(obj)
            case ReportDescriptor():
                result = self.serialize_report_descriptor(obj)
            case ReportPayloadDescriptor():
                result = self.serialize_report_payload_descriptor(obj)
            case Event():
                result = self.serialize_event(obj)
            case EventPayloadDescriptor():
                result = self.serialize_event_payload_descriptor(obj)
            case _:
                result = super().default(obj)
        return result

    def serialize_interval_period(self, obj: IntervalPeriod) -> dict[str, Any]:
        """Serialize an IntervalPeriod object to JSON encodable python."""
        result = {
            "start": self.default(obj.start),
        }

        if obj.duration != datetime.timedelta(seconds=0):
            result["duration"] = create_iso8601_duration(obj.duration)

        if obj.randomize_start != datetime.timedelta(seconds=0):
            result["randomizeStart"] = create_iso8601_duration(obj.randomize_start)

        return result

    def serialize_interval(self, obj: Interval) -> dict[str, Any]:
        """Serialize an Interval object to JSON encodable python."""
        result = {
            "id": obj.id,
            "payloads": _serialize_values_map(obj.payloads),
        }

        if obj.interval_period:
            result["intervalPeriod"] = self.default(obj.interval_period)

        return result

    def serialize_report_data(self, obj: ReportData) -> dict[str, Any]:
        """Serialize a ReportData object to JSON encodable python."""
        result = {
            "resourceName": obj.resource_name,
            "intervals": [self.default(interval) for interval in obj.intervals],
        }

        if obj.interval_period:
            result["intervalPeriod"] = self.default(obj.interval_period)

        return result

    def serialize_report(self, obj: Report) -> dict[str, Any]:
        """Serialize a Report object to JSON encodable python."""
        result = {
            "objectType": "REPORT",
            "programID": obj.program_id,
            "eventID": obj.event_id,
            "clientName": obj.client_name,
            "resources": [self.default(resource) for resource in obj.resources],
        }

        if obj.id is not None:
            result["id"] = obj.id

        if obj.created:
            result["createdDateTime"] = self.default(obj.created)

        if obj.modified:
            result["modificationDateTime"] = self.default(obj.modified)

        if obj.report_name:
            result["reportName"] = obj.report_name

        if obj.payload_descriptors:
            result["payloadDescriptors"] = [
                self.default(payload) for payload in obj.payload_descriptors
            ]

        return result

    def serialize_event(self, obj: Event) -> dict[str, Any]:
        """Serialize an Event object to JSON encodable python."""
        result = {
            "objectType": "EVENT",
            "programID": obj.program_id,
            "intervals": [self.default(interval) for interval in obj.intervals],
        }

        if obj.id is not None:
            result["id"] = obj.id

        if obj.created:
            result["createdDateTime"] = self.default(obj.created)

        if obj.modified:
            result["modificationDateTime"] = self.default(obj.modified)

        if obj.event_name:
            result["eventName"] = obj.event_name

        if obj.priority is not None:
            result["priority"] = obj.priority

        if obj.targets is not None:
            result["targets"] = _serialize_values_map(obj.targets)

        if obj.payload_descriptors:
            result["payloadDescriptors"] = [
                self.default(payload) for payload in obj.payload_descriptors
            ]

        if obj.report_descriptors:
            result["reportDescriptors"] = [
                self.default(report) for report in obj.report_descriptors
            ]

        if obj.interval_period:
            result["intervalPeriod"] = self.default(obj.interval_period)
        return result

    def serialize_report_descriptor(self, obj: ReportDescriptor) -> dict[str, Any]:
        """Serialize a ReportDescriptor object to JSON encodable python."""
        result = {
            "payloadType": obj.payload_type,
        }

        if obj.reading_type:
            result["readingType"] = obj.reading_type

        if obj.units is not None:
            result["units"] = obj.units

        if obj.targets is not None:
            result["targets"] = _serialize_values_map(obj.targets)

        if obj.aggregate is not None:
            result["aggregate"] = obj.aggregate

        if obj.start_interval is not None:
            result["startInterval"] = obj.start_interval

        if obj.num_intervals is not None:
            result["numIntervals"] = obj.num_intervals

        if obj.historical is not None:
            result["historical"] = obj.historical

        if obj.frequency is not None:
            result["frequency"] = obj.frequency

        if obj.repeat is not None:
            result["repeat"] = obj.repeat

        return result

    def serialize_report_payload_descriptor(self, obj: ReportPayloadDescriptor) -> dict[str, Any]:
        """Serialize a ReportPayloadDescriptor object to JSON encodable python."""
        result = {
            "objectType": "REPORT_PAYLOAD_DESCRIPTOR",
            "payloadType": obj.payload_type,
        }

        if obj.reading_type:
            result["readingType"] = obj.reading_type

        if obj.units is not None:
            result["units"] = obj.units

        if obj.accuracy is not None:
            result["accuracy"] = obj.accuracy

        if obj.confidence is not None:
            result["confidence"] = obj.confidence

        return result

    def serialize_event_payload_descriptor(self, obj: EventPayloadDescriptor) -> dict[str, Any]:
        """Serialize a EventPayloadDescriptor object to JSON encodable python."""
        result = {
            "objectType": "EVENT_PAYLOAD_DESCRIPTOR",
            "payloadType": obj.payload_type,
        }

        if obj.units is not None:
            result["units"] = obj.units

        if obj.currency is not None:
            result["currency"] = obj.currency

        return result


def toadr_json_serializer(obj: object) -> str:
    """JSON serializer function for objects in the toadr3 library.

    Can be used in place of the json.dumps in aiohttp.ClientSession.

    Parameters
    ----------
    obj : object
        The object to serialize.

    Returns
    -------
    str
        The serialized object.
    """
    return json.dumps(obj, cls=ToadrJSONEncoder)
