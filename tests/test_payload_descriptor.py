import json

import pytest

from toadr3 import PayloadDescriptor, SchemaException


def test_payload_descriptor():
    data = json.loads(
        """
        {
            "payloadType": "CONSUMPTION_POWER_LIMIT",
            "units": "KW",
            "currency": "NOK"
        }
        """
    )

    payload_descriptor = PayloadDescriptor(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units == "KW"
    assert payload_descriptor.currency == "NOK"


def test_payload_descriptor_defaults():
    data = json.loads("""{"payloadType": "CONSUMPTION_POWER_LIMIT"}""")

    payload_descriptor = PayloadDescriptor(data)

    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units is None
    assert payload_descriptor.currency is None


def test_payload_descriptor_exception_missing_payload_type():
    data = json.loads("""{"units": "KW"}""")

    with pytest.raises(SchemaException) as e:
        PayloadDescriptor(data)

    assert str(e.value) == "Missing 'payloadType' in payload descriptor schema."
