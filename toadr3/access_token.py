import datetime
import os

import aiohttp
from aiohttp import ClientResponse

from .exceptions import ToadrError


class OAuthConfig:
    """Model encapsulating values required for authorization."""

    def __init__(
        self,
        token_url: str,
        grant_type: str,
        scope: str,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        """Encapsulate configuration required for authorization.

        `client_id` and `client_secret` can be None if they are available
        in the environment as CLIENT_ID and CLIENT_SECRET.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp session to use for the request.
        token_url : str
            The URL to acquire the token from.
        grant_type : str
            The grant type to use for the token request.
        scope : str
            The scope of the token.
        client_id : str | None
            The client ID or None if acquirable from the environment as CLIENT_ID.
        client_secret : str | None
            The client secret or None if acquirable from the environment as CLIENT_SECRET.
        """
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._grant_type = grant_type
        self._scope = scope

    @property
    def url(self) -> str:
        """URL to the OAuth server."""
        return self._token_url

    @property
    def client_id(self) -> str | None:
        """Client ID."""
        return self._client_id

    @property
    def client_secret(self) -> str | None:
        """Client secret."""
        return self._client_secret

    @property
    def grant_type(self) -> str:
        """Grant type."""
        return self._grant_type

    @property
    def scope(self) -> str:
        """Scope."""
        return self._scope


class AccessToken:
    """Access token object.

    Enables tracking of expiration time and checking if the token is expired.
    """

    def __init__(self, token: str, expires_in: int):
        """Initialize the access token with an expiration time in seconds.

        Checking if the token is expired can be done with the is_expired() method. The
        is_expired() method will return True if the token is expired or will expire within
        the next 60 seconds.

        Parameters
        ----------
        token : str
            The access token.
        expires_in : int
            The time in seconds until the token expires.
        """
        self._token = token
        time_delta = datetime.timedelta(seconds=expires_in)
        self._expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + time_delta

    @property
    def token(self) -> str:
        """The access token."""
        return self._token

    @property
    def expires_at(self) -> datetime.datetime:
        """The time in seconds until the token expires."""
        return self._expires_at

    @property
    def expires_in(self) -> int:
        """The time in seconds until the token expires."""
        expires_in = self._expires_at - datetime.datetime.now(tz=datetime.timezone.utc)
        return int(expires_in.total_seconds())

    def is_expired(self) -> bool:
        """Check if the token is expired."""
        time_delta = self._expires_at - datetime.datetime.now(tz=datetime.timezone.utc)
        return time_delta < datetime.timedelta(seconds=60)

    def __str__(self) -> str:
        """Return a string representation of the access token."""
        return f"{self.token}"

    def __repr__(self) -> str:
        """Return a string representation of the access token."""
        return f"AccessToken(token='{self.token}', expires_in={self.expires_in})"


async def acquire_access_token_from_config(
    session: aiohttp.ClientSession, config: OAuthConfig
) -> AccessToken:
    """Acquire an access token from the token provider.

    Connect to the token provider and acquire an access token. The access token will be returned
    as an AccessToken object. `client_id` and `client_secret` can be None if they are available
    in the environment as CLIENT_ID and CLIENT_SECRET.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp session to use for the request.
    config: OAuthConfig
        The configuration object required to acquire an access token.

    Returns
    -------
    AccessToken
        The access token object.

    Raises
    ------
    ValueError
        If the `client_id` or `client_secret` are not provided and not available in the environment.
    toadr3.ToadrError
        If the request to the token provider fails.
    """
    return await acquire_access_token(
        session, config.url, config.grant_type, config.scope, config.client_id, config.client_secret
    )


async def acquire_access_token(
    session: aiohttp.ClientSession,
    token_url: str,
    grant_type: str,
    scope: str,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> AccessToken:
    """Acquire an access token from the token provider.

    Connect to the token provider and acquire an access token. The access token will be returned
    as an AccessToken object. `client_id` and `client_secret` can be None if they are available
    in the environment as CLIENT_ID and CLIENT_SECRET.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp session to use for the request.
    token_url : str
        The URL to acquire the token from.
    grant_type : str
        The grant type to use for the token request.
    scope : str
        The scope of the token.
    client_id : str | None
        The client ID or None if acquirable from environment as CLIENT_ID.
    client_secret : str | None
        The client secret or None if acquirable from environment as CLIENT_SECRET.

    Returns
    -------
    AccessToken
        The access token object.

    Raises
    ------
    ValueError
        If the `client_id` or `client_secret` are not provided and not available in the environment.
    toadr3.ToadrError
        If the request to the token provider fails.
    """
    if client_id is None:
        if "CLIENT_ID" not in os.environ:
            raise ValueError("client_id is required")
        client_id = os.getenv("CLIENT_ID")

    if client_secret is None:
        if "CLIENT_SECRET" not in os.environ:
            raise ValueError("client_secret is required")
        client_secret = os.getenv("CLIENT_SECRET")

    if grant_type is None:
        raise ValueError("grant_type is required")

    if scope is None:
        raise ValueError("scope is required")

    credentials = {
        "grant_type": grant_type,
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
    }

    async with session.post(token_url, data=credentials) as response:
        # 400 is the start of HTTP error codes
        if response.status >= 400:  # noqa PLR2004 - Magic value used in comparison
            await _process_error(response)  # will raise a ToadrError

        data = await response.json()
        return AccessToken(data["access_token"], data["expires_in"])


async def _process_error(response: ClientResponse) -> None:
    message = "Failed to acquire access token: "
    json = await response.json()

    if "error" in json:
        message += json["error"]
    else:
        message += json

    raise ToadrError(
        message,
        status_code=response.status,
        reason=response.reason,
        headers=response.headers,  # type: ignore[arg-type]
        json_response=json,
    )
