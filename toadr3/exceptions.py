from typing import Any


class ToadrError(Exception):
    """Exception raised for errors in the Toadr API."""

    def __init__(
        self,
        message: str,
        status_code: int | str,
        reason: str | None = None,
        headers: dict[str, Any] | None = None,
        json_response: dict[str, Any] | None = None,
    ):
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
    def json_response(self) -> dict[str, Any]:
        """The JSON response from the request (full JSON error response, if available)."""
        return self._json_response
