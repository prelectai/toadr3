from .exceptions import SchemaError


class EventPayloadDescriptor:
    """Payload descriptor object to describe the payload of an Event."""

    def __init__(self, data: dict):
        """Create an EventPayloadDescriptor object from parsed JSON data."""
        if "objectType" in data and data["objectType"] != "EVENT_PAYLOAD_DESCRIPTOR":
            raise SchemaError(
                f"Invalid object type '{data['objectType']}' for EventPayloadDescriptor."
            )

        if "payloadType" not in data:
            raise SchemaError("Missing 'payloadType' in payload descriptor schema.")

        self._payload_type = data["payloadType"]
        self._units = data.get("units", None)
        self._currency = data.get("currency", None)

    @property
    def payload_type(self) -> str:
        """The type of the payload."""
        # TODO @jepebe: add enums for payload types found in the OpenADR3 documentation
        #      https://github.com/prelectai/toadr3/issues/25
        return self._payload_type

    @property
    def units(self) -> str | None:
        """The measurement units."""
        return self._units

    @property
    def currency(self) -> str | None:
        """Currency of price payload."""
        return self._currency
