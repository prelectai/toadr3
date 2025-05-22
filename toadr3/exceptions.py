from typing import Any

from .models import Problem


class ToadrError(Exception):
    """Exception raised for errors in the Toadr API."""

    def __init__(
        self,
        message: str,
        status_code: int | str,
        reason: str | None = None,
        headers: dict[str, Any] | None = None,
        json_response: dict[str, Any] | bytes | None = None,
    ):
        super().__init__(message)
        self._message = message

        if isinstance(status_code, str):
            status_code = int(status_code)

        self._status_code: int = status_code
        if reason is None:
            reason = ""
        self._reason = reason
        if headers is None:
            headers = {}
        self._headers = headers
        if json_response is None:
            json_response = {}
        self._json_response = json_response

        if json_response is not None and isinstance(json_response, dict):
            if "error_description" in json_response:
                self.add_note(json_response["error_description"])
        else:
            self.add_note(str(json_response))

    @property
    def message(self) -> str:
        """A short description of the exception."""
        return self._message

    @property
    def status_code(self) -> int:
        """The HTTP status code of the response."""
        return self._status_code

    @property
    def reason(self) -> str:
        """The reason of the exception (message from aiohttp.ClientResponseError)."""
        return self._reason

    @property
    def headers(self) -> dict[str, Any]:
        """The headers of the response."""
        return self._headers

    @property
    def json_response(self) -> dict[str, Any] | bytes | None:
        """The JSON response from the request (full JSON error response, if available)."""
        return self._json_response

    @classmethod
    def from_problem(cls, problem: Problem, status_code: int | None = None) -> "ToadrError":
        """Create a ToadrError from a `Problem` instance.

        Providing `status_code` will override the status code present in the Problem instance.

        Parameters
        ----------
        problem: Problem
            The problem instance
        status_code: int | None
            Override the HTTP status code present in the Problem instance.
        """
        message = problem.title
        if problem.detail is not None:
            message = f"{message}: {problem.detail}"

        if status_code is None:
            try:
                status_code = int(problem.status)
            except ValueError:
                status_code = 0

        return ToadrError(
            message=message,
            status_code=status_code,
            json_response=problem.model_dump(),
        )
