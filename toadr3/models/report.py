import datetime
from typing import Any, Literal

from pydantic import Field

from .docstringbasemodel import DocstringBaseModel
from .event import Event
from .interval import Interval
from .reportdata import ReportData
from .reportpayloaddescriptor import ReportPayloadDescriptor
from .targettype import TargetType
from .valuesmap import ValuesMap


class Report(DocstringBaseModel):
    """Report object for a report."""

    id: str | None = Field(min_length=1, max_length=128, pattern="^[a-zA-Z0-9_-]*$", default=None)
    """VTN provisioned on object creation."""

    created_date_time: datetime.datetime | None = None
    """VTN provisioned on object creation."""

    modification_date_time: datetime.datetime | None = None
    """VTN provisioned on object modification."""

    object_type: Literal["REPORT"] = "REPORT"
    """VTN provisioned on object creation."""

    program_id: str = Field(
        min_length=1, max_length=128, alias="programID", pattern="^[a-zA-Z0-9_-]*$"
    )
    """ID attribute of program object this report is associated with."""

    event_id: str = Field(min_length=1, max_length=128, alias="eventID", pattern="^[a-zA-Z0-9_-]*$")
    """ID attribute of event object this report is associated with."""

    client_name: str = Field(
        min_length=1, max_length=128, alias="clientName", pattern="^[a-zA-Z0-9_-]*$"
    )
    """User generated identifier; may be VEN ID provisioned during program enrollment."""

    report_name: str | None = None
    """User defined string for use in debugging or User Interface."""

    payload_descriptors: list[ReportPayloadDescriptor] | None = None
    """An optional list of objects that provide context to payload types."""

    resources: list[ReportData]

    @property
    def created(self) -> datetime.datetime | None:
        """The time the event was created."""
        return self.created_date_time

    @created.setter
    def created(self, value: datetime.datetime | None) -> None:
        """Set the creation date of the report."""
        self.created_date_time = value

    @property
    def modified(self) -> datetime.datetime | None:
        """The time the event was last modified."""
        return self.modification_date_time

    @modified.setter
    def modified(self, value: datetime.datetime | None) -> None:
        """Set the modification date of the report."""
        self.modification_date_time = value

    @staticmethod
    def create_report(
        event: Event,
        client_name: str,
        report_type: str,
        report_values: list[Any],
        report_name: str | None = None,
        target_type: TargetType | str = TargetType.RESOURCE_NAME,
    ) -> "Report":
        """Create a new report object.

        This will create a single report object for the given event for the specific report types.
        There are several assumptions made in this function:
        1. You want/can only create a report for one report descriptor (at a time).
        2. There is only one target the report applies to.
        3. There is only one interval, and it is specified in an 'intervalPeriod' at the root level.

        Parameters
        ----------
        event : Event
            The event object to create the report for.
        client_name : str
            The client name for the report.
        report_type : str
            The report type for the report (payload type of one of report descriptors).
        report_values : list[Any]
            The report values for the report.
        report_name : str, optional
            The name for the report (for debugging).
        target_type : TargetType | str, optional
            The type of target to look for, the default being TargetType.RESOURCE_NAME.

        Raises
        ------
        ValueError
            For missing and invalid arguments.

        Returns
        -------
        Report
            The created report object.
        """
        if not report_type or not isinstance(report_type, str):
            raise ValueError("report_type is required.")

        if not report_values or not isinstance(report_values, list):
            raise ValueError("report_values is required.")

        if event.targets is None or len(event.targets) == 0:
            raise ValueError("event does not have any targets.")

        if isinstance(target_type, TargetType):
            target_type = target_type.value

        found_resource_name = False
        for target in event.targets:
            if target.type == target_type:
                found_resource_name = True
                break

        if not found_resource_name:
            raise ValueError(f"event does not have a target for type {target_type}.")

        if event.report_descriptors is None or len(event.report_descriptors) == 0:
            raise ValueError("event does not have any report_descriptors.")

        report_descriptor = None
        for rd in event.report_descriptors:
            if rd.payload_type == report_type:
                report_descriptor = rd
                break

        if report_descriptor is None:
            raise ValueError(f"event does not have a report_descriptor for {report_type}.")

        return Report(
            program_id=event.program_id,
            event_id=event.id,
            client_name=client_name,
            report_name=report_name,
            payload_descriptors=[
                ReportPayloadDescriptor.from_report_descriptor(event.report_descriptors[0])
            ],
            resources=[
                ReportData(
                    resource_name=str(event.targets[0].values[0]),
                    interval_period=event.interval_period,
                    intervals=[
                        Interval(
                            id=0,
                            payloads=[
                                ValuesMap(
                                    type=report_type,
                                    values=report_values,
                                )
                            ],
                        )
                    ],
                )
            ],
        )
