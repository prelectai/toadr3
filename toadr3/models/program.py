import datetime
from typing import Literal

from pydantic import AnyUrl, Field

from .docstringbasemodel import DocstringBaseModel
from .eventpayloaddescriptor import EventPayloadDescriptor
from .intervalperiod import IntervalPeriod
from .reportpayloaddescriptor import ReportPayloadDescriptor
from .valuesmap import ValuesMap


class Program(DocstringBaseModel):
    """Provides program specific metadata from VTN to VEN."""

    id: str | None = Field(min_length=1, max_length=128, pattern="^[a-zA-Z0-9_-]*$", default=None)
    """VTN provisioned on object creation."""

    created_date_time: datetime.datetime | None = None
    """VTN provisioned on object creation."""

    modification_date_time: datetime.datetime | None = None
    """VTN provisioned on object modification."""

    object_type: Literal["PROGRAM"] = "PROGRAM"
    """VTN provisioned on object creation."""

    program_name: str = Field(min_length=1, max_length=128)
    """Short name to uniquely identify program."""

    program_long_name: str | None = None
    """Long name of program for human readability."""

    retailer_name: str | None = None
    """Short name of energy retailer providing the program."""

    retailer_long_name: str | None = None
    """Long name of energy retailer for human readability."""

    program_type: str | None = None
    """A program defined categorization."""

    country: str | None = None
    """Alpha-2 code per ISO 3166-1."""

    principal_subdivision: str | None = None
    """Coding per ISO 3166-2. E.g. state in US."""

    time_zone_offset: datetime.timedelta = datetime.timedelta(seconds=0)
    """Number of hours different from UTC for the standard time applicable to the program."""

    interval_period: IntervalPeriod | None = None
    """The temporal span of the program, could be years long."""

    program_descriptions: list[AnyUrl] | None = None
    """A list of program descriptions."""

    binding_events: bool | None = None
    """True if events are fixed once transmitted."""

    local_price: bool | None = None
    """True if events have been adapted from a grid event."""

    payload_descriptors: list[EventPayloadDescriptor | ReportPayloadDescriptor] | None = None
    """A list of payloadDescriptors."""

    targets: list[ValuesMap] | None = None
    """A list of valuesMap objects."""
