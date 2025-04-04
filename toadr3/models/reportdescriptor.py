from pydantic import Field

from .docstringbasemodel import DocstringBaseModel
from .valuesmap import ValuesMap


class ReportDescriptor(DocstringBaseModel):
    """An object that may be used to request a report from a VEN."""

    payload_type: str = Field(min_length=1, max_length=128)
    """The type of the payload."""

    reading_type: str | None = None
    """Enumerated or private string signifying the type of reading."""

    units: str | None = None
    """The measurement units of the reading."""

    targets: list[ValuesMap] | None = None
    """A list of ValuesMap objects."""

    aggregate: bool = False
    """Whether the report should be aggregated.

    True if report should aggregate results from all targeted resources.
    False if report includes results for each resource.
    """

    start_interval: int = -1
    """The interval at which to generate the report (-1 means end of last)."""

    num_intervals: int = -1
    """The number of intervals to include in a report.

    -1 indicates that all intervals are to be included.
    """

    historical: bool = True
    """Whether the report is historical or not.

    True indicates report on intervals preceding startInterval.
    False indicates report on intervals following startInterval (e.g. forecast).
    """

    frequency: int = -1
    """The frequency of the report.

     Number of intervals that elapse between reports.
    -1 indicates same as numIntervals.
    """

    repeat: int = 1
    """The number of times to repeat the report.

    1 indicates generate one report.
    -1 indicates repeat indefinitely.
    """
