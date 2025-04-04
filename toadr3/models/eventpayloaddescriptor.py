from typing import Literal

from pydantic import Field

from toadr3.models import DocstringBaseModel


class EventPayloadDescriptor(DocstringBaseModel):
    """Contextual information used to interpret event valuesMap values."""

    object_type: Literal["EVENT_PAYLOAD_DESCRIPTOR"] = "EVENT_PAYLOAD_DESCRIPTOR"
    """Used as discriminator."""

    payload_type: str = Field(min_length=1, max_length=128)
    """Enumerated or private string signifying the nature of values."""

    units: str | None = None
    """The measurement units of the payload."""

    currency: str | None = None
    """The currency of the payload, if applicable."""
