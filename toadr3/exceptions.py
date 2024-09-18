class ToadrError(Exception):
    """Exception raised for errors in the Toadr API."""

    def __init__(
        self,
        message: str,
        status_code: int | str,
        reason: str | None = None,
        headers: dict | None = None,
        json_response: dict | None = None,
    ):
        self._message = message

        if isinstance(status_code, str):
            status_code = int(status_code)

        self._status_code: int = status_code
        self._reason = reason
        self._headers = headers
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
    def headers(self) -> dict:
        """The headers of the response."""
        return self._headers

    @property
    def json_response(self) -> dict:
        """The JSON response from the request (full JSON error response, if available)."""
        return self._json_response


class SchemaError(Exception):
    """Exception raised for schema errors in the Toadr API."""

    def __init__(self, message: str):
        self._message = message

    @property
    def message(self) -> str:
        """A short description of the exception."""
        return self._message
