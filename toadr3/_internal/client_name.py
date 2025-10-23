from typing import Any

from .query_parameter import QueryParameter, QueryParams


class ClientName(QueryParameter):
    """Client name query parameter.

    client_name : str | None
        The client name to filter the items by.
    """

    @staticmethod
    def create_query_parameters(params: QueryParams, args: dict[str, Any]) -> None:
        """Add client_name parameter."""
        if "client_name" in args and args["client_name"] is not None:
            params["clientName"] = args["client_name"]

    @staticmethod
    def check_query_parameters(errors: list[str], args: dict[str, Any]) -> None:
        """Check if client_name parameter is valid."""
        # nothing to check
