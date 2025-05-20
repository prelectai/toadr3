import asyncio

from aiohttp import ClientSession

import toadr3


class ToadrClient:
    """Client to interact with OpenADR3 VTN servers.

    If the client created its own session during initialization, the client needs to
    be closed before shutdown.
    """

    def __init__(
        self,
        vtn_url: str,
        oauth_config: toadr3.OAuthConfig | None,
        session: ClientSession | None = None,
    ) -> None:
        """Initialize the client.

        Parameters
        ----------
        vtn_url : str
            The URL of the VTN server to connect to.
        oauth_config : toadr3.OAuthConfig | None
            The OAuth configuration to use or None if credentials are not required.
        session : ClientSession | None
            The session to use or None if the client should make its own session.
        """
        self._vtn_url = vtn_url.rstrip("/")
        self._oauth_config = oauth_config
        self._session = session if session is not None else ClientSession()
        self._token_lock = asyncio.Lock()
        self._token: toadr3.AccessToken | None = None

    @property
    def client_session(self) -> ClientSession:
        """Client session for the Switch API."""
        return self._session

    @property
    def vtn_url(self) -> str:
        """VTN server URL."""
        return self._vtn_url

    async def _fetch_token(self) -> toadr3.AccessToken | None:
        """Fetch an access token from the OAuth2 server."""
        if self._oauth_config is None:
            return None
        return await toadr3.acquire_access_token_from_config(self._session, self._oauth_config)

    @property
    async def token(self) -> toadr3.AccessToken | None:
        """Access token for the Switch API."""
        async with self._token_lock:
            if self._token is None or self._token.is_expired():
                self._token = await self._fetch_token()

            return self._token

    async def close(self) -> None:
        """Close the client session."""
        await self._session.close()
