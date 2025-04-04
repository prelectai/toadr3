import pytest
from pydantic import ValidationError

from toadr3.models import ReportPayloadDescriptor


def test_report_payload_descriptor() -> None:
    data = """
        {
            "payloadType": "CONSUMPTION_POWER_LIMIT",
            "readingType": "DIRECT_READ",
            "units": "KW",
            "accuracy": 1.5,
            "confidence": 2
        }
        """

    payload_descriptor = ReportPayloadDescriptor.model_validate_json(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.reading_type == "DIRECT_READ"
    assert payload_descriptor.units == "KW"
    assert payload_descriptor.accuracy == 1.5
    assert payload_descriptor.confidence == 2


def test_report_payload_descriptor_defaults() -> None:
    data = """{"payloadType": "CONSUMPTION_POWER_LIMIT"}"""

    payload_descriptor = ReportPayloadDescriptor.model_validate_json(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.reading_type is None
    assert payload_descriptor.accuracy is None
    assert payload_descriptor.confidence is None


def test_report_payload_descriptor_exception_missing_payload_type() -> None:
    data = """{"units": "KW"}"""

    with pytest.raises(ValidationError):
        ReportPayloadDescriptor.model_validate_json(data)


def test_report_payload_descriptor_exception_invalid_object_type() -> None:
    data = """
        {
            "objectType": "INVALID",
            "payloadType": "CONSUMPTION_POWER_LIMIT"
        }
        """

    with pytest.raises(ValidationError):
        ReportPayloadDescriptor.model_validate_json(data)


def test_report_payload_descriptor_correct_object_type() -> None:
    data = """
        {
            "objectType": "REPORT_PAYLOAD_DESCRIPTOR",
            "payloadType": "CONSUMPTION_POWER_LIMIT"
        }
        """

    payload_descriptor = ReportPayloadDescriptor.model_validate_json(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.reading_type is None
    assert payload_descriptor.accuracy is None
    assert payload_descriptor.confidence is None
