import re
from typing import Any

from .query_parameter import QueryParameter, QueryParams

_regex = re.compile(r"^[a-zA-Z0-9_-]*$")


class ObjectID(QueryParameter):
    """Object ID query parameter.

    Represents an object ID, for example program_id or event_id.
    """

    _attribute = ("unset", "unset")
    """Override this to provide class specific values.

    The first version represent the input argument, for example: 'value_id'
    The second value represent the query parameter, for example: 'valueID'
    """

    _nullable = True
    """Override this to disable nullable values."""

    @classmethod
    def create_query_parameters(cls, params: QueryParams, args: dict[str, Any]) -> None:
        """Add a parameter that is an object ID."""
        arg = cls._attribute[0]
        if arg in args and args[arg] is not None:
            params[cls._attribute[1]] = args[arg]

    @classmethod
    def check_query_parameters(cls, errors: list[str], args: dict[str, Any]) -> None:
        """Check if the ObjectID parameter is valid."""
        arg = cls._attribute[0]
        object_id = args[arg]

        if not cls._nullable and object_id is None:
            errors.append(f"{arg} cannot be None")
            return

        if object_id is not None:
            if not isinstance(object_id, str):
                errors.append(f"{arg} must be a string")
                return

            if not 1 <= len(object_id) <= 128:  # noqa: PLR2004
                errors.append(f"{arg} must be between 1 and 128 characters long")

            if _regex.match(object_id) is None:
                msg = f"{arg} '{object_id}' does not match regex '{_regex.pattern}'"
                errors.append(msg)


class ProgramID(ObjectID):
    """Program ID query parameter.

    program_id : str | None
        The program ID to filter the items by.
    """

    _attribute = ("program_id", "programID")


class EventID(ObjectID):
    """Event ID query parameter.

    event_id : str | None
        The event ID to filter the items by.
    """

    _attribute = ("event_id", "eventID")


class SubscriptionID(ObjectID):
    """Subscription ID query parameter."""

    _attribute = ("subscription_id", "subscriptionID")
    _nullable = False
