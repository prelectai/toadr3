from typing import Any

from toadr3.models import TargetType

from .query_parameter import QueryParameter, QueryParams


class Targets(QueryParameter):
    """Target type and target value parameters.

    target_type : TargetType | str | None
        The target type to filter the results by.
    target_values : list[str] | None
        The target values to filter the results by (names of the target type).
    """

    @staticmethod
    def create_query_parameters(params: QueryParams, args: dict[str, Any]) -> None:
        """Add target type and target value parameters."""
        target_type = args.get("target_type")
        target_values = args.get("target_values")

        if target_type is not None and target_values is not None:
            if isinstance(target_type, TargetType):
                params["targetType"] = target_type.value
            else:
                params["targetType"] = target_type  # should be string

            params["targetValues"] = target_values

    @staticmethod
    def check_query_parameters(errors: list[str], args: dict[str, Any]) -> None:
        """Check if skip and limit parameters are valid."""
        target_type = args.get("target_type")
        target_values = args.get("target_values")

        if target_type is not None and target_values is None:
            errors.append("target_values are required when target_type is provided")

        if target_values is not None and target_type is None:
            errors.append("target_type is required when target_values are provided")

        if target_values is not None and not isinstance(target_values, list):
            errors.append("target_values must be a list of strings")

        if target_type is not None and not isinstance(target_type, (TargetType, str)):
            errors.append("target_type must be TargetType or str")
