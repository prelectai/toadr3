import json

import pytest

from toadr3 import ReportPayloadDescriptor, SchemaError


def test_report_payload_descriptor():
    data = json.loads(
        """
        {
            "payloadType": "CONSUMPTION_POWER_LIMIT",
            "readingType": "DIRECT_READ",
            "units": "KW",
            "accuracy": 1.5,
            "confidence": 2
        }
        """
    )

    payload_descriptor = ReportPayloadDescriptor(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.reading_type == "DIRECT_READ"
    assert payload_descriptor.units == "KW"
    assert payload_descriptor.accuracy == 1.5
    assert payload_descriptor.confidence == 2


def test_report_payload_descriptor_defaults():
    data = json.loads("""{"payloadType": "CONSUMPTION_POWER_LIMIT"}""")

    payload_descriptor = ReportPayloadDescriptor(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.reading_type is None
    assert payload_descriptor.accuracy is None
    assert payload_descriptor.confidence is None


def test_report_payload_descriptor_exception_missing_payload_type():
    data = json.loads("""{"units": "KW"}""")

    with pytest.raises(SchemaError) as e:
        ReportPayloadDescriptor(data)

    assert str(e.value) == "Missing 'payloadType' in payload descriptor schema."


def test_report_payload_descriptor_exception_invalid_object_type():
    data = json.loads(
        """
        {
            "objectType": "INVALID",
            "payloadType": "CONSUMPTION_POWER_LIMIT"
        }
        """
    )

    with pytest.raises(SchemaError) as e:
        ReportPayloadDescriptor(data)

    assert str(e.value) == "Invalid object type 'INVALID' for ReportPayloadDescriptor."


def test_report_payload_descriptor_correct_object_type():
    data = json.loads(
        """
        {
            "objectType": "REPORT_PAYLOAD_DESCRIPTOR",
            "payloadType": "CONSUMPTION_POWER_LIMIT"
        }
        """
    )

    payload_descriptor = ReportPayloadDescriptor(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.reading_type is None
    assert payload_descriptor.accuracy is None
    assert payload_descriptor.confidence is None
