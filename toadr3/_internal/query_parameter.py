from abc import ABC, abstractmethod
from typing import Any, TypeAlias

QueryParams: TypeAlias = dict[str, str | int | list[str]]


class QueryParameter(ABC):
    """QueryParameter base class."""

    @staticmethod
    @abstractmethod
    def create_query_parameters(params: QueryParams, args: dict[str, Any]) -> None:
        """Process incoming arguments into query parameters."""

    @staticmethod
    @abstractmethod
    def check_query_parameters(errors: list[str], args: dict[str, Any]) -> None:
        """Check if query parameter is valid."""
