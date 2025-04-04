from pydantic import Field

from .docstringbasemodel import DocstringBaseModel
from .interval import Interval
from .intervalperiod import IntervalPeriod


class ReportData(DocstringBaseModel):
    """Report data associated with a resource."""

    resource_name: str = Field(min_length=1, max_length=128)
    """The name of the resource.

    A value of AGGREGATED_REPORT indicates an aggregation of more that one resource's data.
    """

    interval_period: IntervalPeriod | None = None
    """Defines default start and durations of intervals."""

    intervals: list[Interval]
    """List of interval objects."""
