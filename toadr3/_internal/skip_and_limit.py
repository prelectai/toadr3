from typing import Any

from .query_parameter import QueryParameter, QueryParams


class SkipAndLimit(QueryParameter):
    """Skip and limit parameters.

    skip : int | None
        The number of items to skip (for pagination).
    limit : int | None
        The maximum number of items to return.
    """

    @staticmethod
    def create_query_parameters(params: QueryParams, args: dict[str, Any]) -> None:
        """Add skip and limit parameters."""
        if "skip" in args and args["skip"] is not None:
            params["skip"] = args["skip"]

        if "limit" in args and args["limit"] is not None:
            params["limit"] = args["limit"]

    @staticmethod
    def check_query_parameters(errors: list[str], args: dict[str, Any]) -> None:
        """Check if skip and limit parameters are valid."""
        skip = args.get("skip")
        limit = args.get("limit")

        if skip is not None:
            if not isinstance(skip, int):
                errors.append("skip must be an integer")
            elif skip < 0:
                errors.append("skip must be a positive integer")

        if limit is not None:
            if not isinstance(limit, int):
                errors.append("limit must be an integer")
            elif limit < 0:
                errors.append("limit must be a positive integer")
