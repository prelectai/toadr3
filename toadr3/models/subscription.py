import datetime
from typing import Literal

from pydantic import Field

from .docstringbasemodel import DocstringBaseModel
from .objectoperation import ObjectOperation
from .valuesmap import ValuesMap


class Subscription(DocstringBaseModel):
    """An object created by a client to receive notification of operations on objects.

    Clients may subscribe to be notified when a type of object is created,
    updated, or deleted.
    """

    id: str | None = Field(min_length=1, max_length=128, pattern="^[a-zA-Z0-9_-]*$", default=None)
    """VTN provisioned on object creation."""

    created_date_time: datetime.datetime | None = None
    """VTN provisioned on object creation."""

    modification_date_time: datetime.datetime | None = None
    """VTN provisioned on object modification."""

    object_type: Literal["SUBSCRIPTION"] = "SUBSCRIPTION"
    """Used as discriminator."""

    client_name: str = Field(min_length=1, max_length=128)
    """User generated identifier; may be VEN ID provisioned during program enrollment."""

    program_id: str = Field(
        min_length=1, max_length=128, alias="programID", pattern="^[a-zA-Z0-9_-]*$"
    )
    """ID attribute of program object this event is associated with."""

    object_operations: list[ObjectOperation]
    """List of objects and operations to subscribe to."""

    targets: list[ValuesMap] | None = None
    """A list of valuesMap objects.

    Used by server to filter callbacks.
    """

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
