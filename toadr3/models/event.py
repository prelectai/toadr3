import datetime
from typing import Literal

from pydantic import Field

from .docstringbasemodel import DocstringBaseModel
from .eventpayloaddescriptor import EventPayloadDescriptor
from .interval import Interval
from .intervalperiod import IntervalPeriod
from .reportdescriptor import ReportDescriptor
from .valuesmap import ValuesMap


class Event(DocstringBaseModel):
    """Event object to communicate a Demand Response request to VEN.

    If intervalPeriod is present, sets start time and duration of intervals.
    """

    id: str | None = Field(min_length=1, max_length=128, pattern="^[a-zA-Z0-9_-]*$", default=None)
    """VTN provisioned on object creation."""

    created_date_time: datetime.datetime | None = None
    """VTN provisioned on object creation."""

    modification_date_time: datetime.datetime | None = None
    """VTN provisioned on object modification."""

    object_type: Literal["EVENT"] = "EVENT"
    """VTN provisioned on object creation."""

    program_id: str = Field(
        min_length=1, max_length=128, alias="programID", pattern="^[a-zA-Z0-9_-]*$"
    )
    """ID attribute of program object this event is associated with."""

    event_name: str | None = None
    """User defined string for use in debugging or User Interface."""

    priority: int | None = None
    """Relative priority of event.

    A lower number is a higher priority.
    """
    targets: list[ValuesMap] | None = None
    """A list of valuesMap objects."""

    report_descriptors: list[ReportDescriptor] | None = None
    """A list of reportDescriptor objects.

    Used to request reports from VEN.
    """

    payload_descriptors: list[EventPayloadDescriptor] | None = None
    """A list of payloadDescriptor objects."""

    interval_period: IntervalPeriod | None = None
    """Defines default start and durations of intervals."""

    intervals: list[Interval]
    """List of interval objects."""

    @property
    def created(self) -> datetime.datetime | None:
        """The time the event was created."""
        return self.created_date_time

    @created.setter
    def created(self, value: datetime.datetime | None) -> None:
        """Set the creation date of the event."""
        self.created_date_time = value

    @property
    def modified(self) -> datetime.datetime | None:
        """The time the event was last modified."""
        return self.modification_date_time

    @modified.setter
    def modified(self, value: datetime.datetime | None) -> None:
        """Set the modification date of the event."""
        self.modification_date_time = value
