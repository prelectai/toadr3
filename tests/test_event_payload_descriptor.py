import json

import pytest

from toadr3 import EventPayloadDescriptor, SchemaError


def test_event_payload_descriptor():
    data = json.loads(
        """
        {
            "payloadType": "CONSUMPTION_POWER_LIMIT",
            "units": "KW",
            "currency": "NOK"
        }
        """
    )

    payload_descriptor = EventPayloadDescriptor(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units == "KW"
    assert payload_descriptor.currency == "NOK"


def test_event_payload_descriptor_defaults():
    data = json.loads("""{"payloadType": "CONSUMPTION_POWER_LIMIT"}""")

    payload_descriptor = EventPayloadDescriptor(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.currency is None


def test_event_payload_descriptor_exception_missing_payload_type():
    data = json.loads("""{"units": "KW"}""")

    with pytest.raises(SchemaError) as e:
        EventPayloadDescriptor(data)

    assert str(e.value) == "Missing 'payloadType' in payload descriptor schema."


def test_event_payload_descriptor_exception_invalid_object_type():
    data = json.loads(
        """
        {
            "objectType": "INVALID",
            "payloadType": "CONSUMPTION_POWER_LIMIT"
        }
        """
    )

    with pytest.raises(SchemaError) as e:
        EventPayloadDescriptor(data)

    assert str(e.value) == "Invalid object type 'INVALID' for EventPayloadDescriptor."


def test_event_payload_descriptor_correct_object_type():
    data = json.loads(
        """
        {
            "objectType": "EVENT_PAYLOAD_DESCRIPTOR",
            "payloadType": "CONSUMPTION_POWER_LIMIT"
        }
        """
    )

    payload_descriptor = EventPayloadDescriptor(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.currency is None
