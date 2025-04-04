from typing import Literal

from pydantic import Field

from .docstringbasemodel import DocstringBaseModel
from .reportdescriptor import ReportDescriptor


class ReportPayloadDescriptor(DocstringBaseModel):
    """Contextual information used to interpret report payload values."""

    object_type: Literal["REPORT_PAYLOAD_DESCRIPTOR"] = "REPORT_PAYLOAD_DESCRIPTOR"
    """Used as discriminator."""

    payload_type: str = Field(min_length=1, max_length=128)
    """Enumerated or private string signifying the nature of values."""

    reading_type: str | None = None
    """Enumerated or private string signifying the type of reading."""

    units: str | None = None
    """Units of measure."""

    accuracy: float | None = None
    """A quantification of the accuracy of a set of payload values."""

    confidence: int | None = Field(ge=0, le=100, default=None)
    """A quantification of the confidence of a set of payload values."""

    @staticmethod
    def from_report_descriptor(report_descriptor: ReportDescriptor) -> "ReportPayloadDescriptor":
        """Create a ReportPayloadDescriptor from a ReportDescriptor."""
        return ReportPayloadDescriptor(
            payload_type=report_descriptor.payload_type,
            reading_type=report_descriptor.reading_type,
            units=report_descriptor.units,
        )
