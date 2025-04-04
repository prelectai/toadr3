from pydantic import Field

from toadr3.models import DocstringBaseModel


class Point(DocstringBaseModel):
    """A pair of floats typically used as a point on a 2 dimensional grid."""

    x: float
    """The x coordinate of the point."""

    y: float
    """The y coordinate of the point."""


class ValuesMap(DocstringBaseModel):
    """Represents one or more values associated with a type."""

    type: str = Field(min_length=1, max_length=128)
    """Enumerated or private string signifying the nature of values."""

    values: list[int | float | str | bool | Point]
    """A list of data points. Most often a singular value such as a price."""
