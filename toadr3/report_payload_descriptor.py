from .exceptions import SchemaError


class ReportPayloadDescriptor:
    """Payload descriptor object to describe the payload of a Report."""

    def __init__(self, data: dict):
        """Create a new EventPayloadDescriptor object from JSON data."""
        if "objectType" in data and data["objectType"] != "REPORT_PAYLOAD_DESCRIPTOR":
            raise SchemaError(
                f"Invalid object type '{data['objectType']}' for ReportPayloadDescriptor."
            )

        if "payloadType" not in data:
            raise SchemaError("Missing 'payloadType' in payload descriptor schema.")

        self._payload_type = data["payloadType"]
        self._reading_type = data.get("readingType", None)
        self._units = data.get("units", None)
        self._accuracy = None
        self._confidence = None

        if "accuracy" in data:
            self._accuracy = float(data["accuracy"])

        if "confidence" in data:
            self._confidence = int(data["confidence"])

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
    def reading_type(self) -> str | None:
        """The reading type."""
        return self._reading_type

    @property
    def accuracy(self) -> float | None:
        """Quantification of the accuracy of the readings."""
        return self._accuracy

    @property
    def confidence(self) -> int | None:
        """Quantification of the confidence of the readings."""
        return self._confidence
