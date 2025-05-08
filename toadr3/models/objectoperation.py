from enum import StrEnum

from toadr3.models import DocstringBaseModel


class ObjectType(StrEnum):
    """Types of objects addressable through API."""

    EVENT = "EVENT"
    PROGRAM = "PROGRAM"
    REPORT = "REPORT"
    RESOURCE = "RESOURCE"
    SUBSCRIPTION = "SUBSCRIPTION"
    VEN = "VEN"


class OperationType(StrEnum):
    """Object operation to subscribe to."""

    DELETE = "DELETE"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


class ObjectOperation(DocstringBaseModel):
    """Object type, operations, and callbackUrl."""

    objects: list[ObjectType]
    """List of objects to subscribe to."""

    operations: list[OperationType]
    """List of operations to subscribe to."""

    callback_url: str
    """User provided webhook URL."""

    bearer_token: str | None = None
    """User provided token.

    To avoid custom integrations, callback endpoints should accept the provided bearer
    token to authenticate VTN requests.
    """
