import asyncio

from aiohttp import ClientSession

import toadr3


class ToadrClient:
    """Client to interact with OpenADR3 VTN servers."""

    def __init__(
        self,
        vtn_url: str,
        oauth_config: toadr3.OAuthConfig,
        session: ClientSession | None = None,
    ) -> None:
        self._vtn_url = vtn_url
        self._oauth_config = oauth_config
        self._session = session if session is not None else ClientSession()
        self._token_lock = asyncio.Lock()
        self._token: toadr3.AccessToken | None = None

    @property
    def client_session(self) -> ClientSession:
        """Client session for the Switch API."""
        return self._session

    async def _fetch_token(self) -> toadr3.AccessToken:
        """Fetch an access token from the OAuth2 server."""
        return await toadr3.acquire_access_token_from_config(self._session, self._oauth_config)

    @property
    async def token(self) -> toadr3.AccessToken:
        """Access token for the Switch API."""
        async with self._token_lock:
            if self._token is None or self._token.is_expired():
                self._token = await self._fetch_token()

            return self._token

    async def close(self) -> None:
        """Close the client session."""
        await self._session.close()
