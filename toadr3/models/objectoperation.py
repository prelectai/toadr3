from enum import StrEnum

from toadr3.models import DocstringBaseModel


class ObjectTypes(StrEnum):
    """Types of objects addressable through API."""

    EVENT = "EVENT"
    PROGRAM = "PROGRAM"
    REPORT = "REPORT"
    RESOURCE = "RESOURCE"
    SUBSCRIPTION = "SUBSCRIPTION"
    VEN = "VEN"


class OperationTypes(StrEnum):
    """Object operation to subscribe to."""

    DELETE = "DELETE"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


class ObjectOperation(DocstringBaseModel):
    """Object type, operations, and callbackUrl."""

    objects: list[ObjectTypes]
    """List of objects to subscribe to."""

    operations: list[OperationTypes]
    """List of operations to subscribe to."""

    callback_url: str
    """User provided webhook URL."""

    bearer_token: str | None = None
    """User provided token.

    To avoid custom integrations, callback endpoints should accept the provided bearer
    token to authenticate VTN requests.
    """
