from typing import Any

from .query_parameter import QueryParameter, QueryParams


class ParameterBuilder:
    def __init__(self, *parameter_types: type[QueryParameter]) -> None:
        self._parameter_types = parameter_types

    def check_query_parameters(self, args: dict[str, Any]) -> None:
        """Check query parameters.

        Parameters
        ----------
        args : dict[str, Any]
            Arguments passed as query parameters.

        Raises
        ------
        ValueError
            If the query parameters are invalid.
        """
        errors: list[str] = []
        for parameter in self._parameter_types:
            parameter.check_query_parameters(errors, args)

        if errors:
            raise ValueError(", ".join(errors))

    def build_query_parameters(
        self, args: dict[str, Any], extra_params: QueryParams | None
    ) -> QueryParams:
        """Build query parameters."""
        parameters: QueryParams = {}

        if extra_params is not None:
            parameters = extra_params.copy()

        for parameter in self._parameter_types:
            parameter.create_query_parameters(parameters, args)
        return parameters
