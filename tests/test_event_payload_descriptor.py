import pytest
from pydantic import ValidationError

from toadr3.models import EventPayloadDescriptor


def test_event_payload_descriptor() -> None:
    data = '{"payloadType":"CONSUMPTION_POWER_LIMIT","units":"KW","currency":"NOK"}'

    payload_descriptor = EventPayloadDescriptor.model_validate_json(data)

    assert payload_descriptor.object_type == "EVENT_PAYLOAD_DESCRIPTOR"
    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units == "KW"
    assert payload_descriptor.currency == "NOK"


def test_event_payload_descriptor_defaults() -> None:
    data = '{"payloadType": "CONSUMPTION_POWER_LIMIT"}'

    payload_descriptor = EventPayloadDescriptor.model_validate_json(data)

    assert payload_descriptor.object_type == "EVENT_PAYLOAD_DESCRIPTOR"
    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.currency is None


def test_event_payload_descriptor_exception_missing_payload_type() -> None:
    data = '{"units": "KW"}'

    with pytest.raises(ValidationError):
        EventPayloadDescriptor.model_validate_json(data)


def test_event_payload_descriptor_exception_invalid_object_type() -> None:
    data = """
        {
            "objectType": "INVALID",
            "payloadType": "CONSUMPTION_POWER_LIMIT"
        }
        """

    with pytest.raises(ValidationError):
        EventPayloadDescriptor.model_validate_json(data)


def test_event_payload_descriptor_correct_object_type() -> None:
    data = '{"objectType":"EVENT_PAYLOAD_DESCRIPTOR","payloadType":"CONSUMPTION_POWER_LIMIT"}'

    payload_descriptor = EventPayloadDescriptor.model_validate_json(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.currency is None

    json = payload_descriptor.model_dump_json()
    assert json == (
        '{"objectType":"EVENT_PAYLOAD_DESCRIPTOR",'
        '"payloadType":"CONSUMPTION_POWER_LIMIT",'
        '"units":null,'
        '"currency":null}'
    )


def test_event_payload_descriptor_incorrect_object_type() -> None:
    data = """
        {
            "objectType": "EVENT_PAYLOAD_DESCR",
            "payloadType": "CONSUMPTION_POWER_LIMIT"
        }
        """

    with pytest.raises(ValidationError):
        EventPayloadDescriptor.model_validate_json(data)
