import asyncio
from types import TracebackType
from typing import Literal, Self

from aiohttp import ClientSession

import toadr3
from toadr3.models import Event, ObjectType, Program, Report, Subscription, TargetType


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
        self._closed = False

    @property
    def client_session(self) -> ClientSession:
        """Client session for the Switch API."""
        return self._session

    @property
    def vtn_url(self) -> str:
        """VTN server URL."""
        return self._vtn_url

    @property
    def closed(self) -> bool:
        """Whether or not the client is closed."""
        return self._closed

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

    async def get_events(
        self,
        program_id: str | None = None,
        target_type: TargetType | str | None = None,
        target_values: list[str] | None = None,
        skip: int | None = None,
        limit: int | None = None,
        extra_params: dict[str, str | int | list[str]] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> list[Event]:
        """Get a list of events from the VTN.

        Lists all the events available from the VTN.
        The results can be filtered by providing a program ID, and/or target type and target values.

        Parameters
        ----------
        program_id : str | None
            The program ID to filter the events by.
        target_type : TargetType | str | None
            The target type to filter the events by.
        target_values : list[str] | None
            The target values to filter the events by (names of the target type).
        skip : int | None
            The number of events to skip (for pagination).
        limit : int | None
            The maximum number of events to return.
        extra_params : dict[str, str | int | list[str]] | None
            Extra query parameters to include in the request.
        custom_headers : dict[str, str] | None
            Extra headers to include in the request.

        Returns
        -------
        list[Event]
            A list of events.

        Raises
        ------
        ValueError
            If the query parameters are invalid.
        toadr3.ToadrError
            If the request to the VTN fails. Specifically, response status 400, 403, or 500,
        aiohttp.ClientError
            If there is an unexpected error with the HTTP request to the VTN.
        """
        return await toadr3.get_events(
            session=self._session,
            vtn_url=self._vtn_url,
            access_token=await self.token,
            program_id=program_id,
            target_type=target_type,
            target_values=target_values,
            skip=skip,
            limit=limit,
            extra_params=extra_params,
            custom_headers=custom_headers,
        )

    async def get_programs(
        self,
        target_type: TargetType | str | None = None,
        target_values: list[str] | None = None,
        skip: int | None = None,
        limit: int | None = None,
        extra_params: dict[str, str | int | list[str]] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> list[Program]:
        """Get a list of programs from the VTN.

        List all programs known to the server.
        Use skip and pagination query params to limit response size.

        Parameters
        ----------
        target_type: TargetType | str | None
            The target type to filter the programs by.
        target_values: list[str] | None
            The target values to filter the programs by (names of the target type).
        skip: int | None
            The number of programs to skip (for pagination).
        limit: int | None
            The maximum number of programs to return.
        extra_params: dict[str, str | int | list[str]] | None
            Extra query parameters to include in the request.
        custom_headers: dict[str, str] | None
            Extra headers to include in the request.

        Returns
        -------
        list[Program]
            A list of programs.

        Raises
        ------
        ValueError
            If the query parameters are invalid.
        toadr3.ToadrError
            If the request to the VTN fails. Specifically, response status 400, 403, or 500,
        aiohttp.ClientError
            If there is an unexpected error with the HTTP request to the VTN.
        """
        return await toadr3.get_programs(
            session=self._session,
            vtn_url=self._vtn_url,
            access_token=await self.token,
            target_type=target_type,
            target_values=target_values,
            skip=skip,
            limit=limit,
            extra_params=extra_params,
            custom_headers=custom_headers,
        )

    async def get_subscriptions(
        self,
        program_id: str | None = None,
        client_name: str | None = None,
        target_type: TargetType | str | None = None,
        target_values: list[str] | None = None,
        objects: list[str] | list[ObjectType] | None = None,
        skip: int | None = None,
        limit: int | None = None,
        extra_params: dict[str, str | int | list[str]] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> list[Subscription]:
        """List all subscriptions.

        May filter results by programID and clientID as query params.
        May filter results by objects as query param. See objectTypes schema.
        Use skip and pagination query params to limit response size.

        Parameters
        ----------
        program_id : str | None
            The program ID to filter the subscriptions by.
        client_name : str | None
            The client name to filter the subscriptions by.
        target_type: TargetType | str | None
            The target type to filter the subscriptions by.
        target_values: list[str] | None
            The target values to filter the subscriptions by (names of the target type).
        objects: list[str] | list[ObjectType] | None
            The object types to filter the subscriptions by.
        skip: int | None
            The number of subscriptions to skip (for pagination).
        limit: int | None
            The maximum number of subscriptions to return.
        extra_params: dict[str, str | int | list[str]] | None
            Extra query parameters to include in the request.
        custom_headers: dict[str, str] | None
            Extra headers to include in the request.

        Returns
        -------
        list[Subscription]
            A list of subscriptions.

        Raises
        ------
        ValueError
            If the query parameters are invalid.
        toadr3.ToadrException
            If the request to the VTN fails. Specifically, response status 400, 403, or 500,
        aiohttp.ClientError
            If there is an unexpected error with the HTTP request to the VTN.
        """
        return await toadr3.get_subscriptions(
            session=self._session,
            vtn_url=self._vtn_url,
            access_token=await self.token,
            program_id=program_id,
            client_name=client_name,
            target_type=target_type,
            target_values=target_values,
            objects=objects,
            skip=skip,
            limit=limit,
            extra_params=extra_params,
            custom_headers=custom_headers,
        )

    async def post_subscription(
        self,
        subscription: Subscription,
        custom_headers: dict[str, str] | None = None,
    ) -> Subscription:
        """Create a new subscription.

        Parameters
        ----------
        subscription: Subscription
            The subscription to create.
        custom_headers: dict[str, str] | None
            Extra headers to include in the request.

        Returns
        -------
        Subscription
            The subscription object created by the VTN.

        Raises
        ------
        ValueError
            If the query parameters are invalid.
        toadr3.ToadrException
            If the request to the VTN fails. Specifically, response status 400, 403, or 500,
        aiohttp.ClientError
            If there is an unexpected error with the HTTP request to the VTN.

        """
        return await toadr3.post_subscription(
            session=self._session,
            vtn_url=self._vtn_url,
            access_token=await self.token,
            subscription=subscription,
            custom_headers=custom_headers,
        )

    async def get_reports(
        self,
        program_id: str | None = None,
        event_id: str | None = None,
        client_name: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
        extra_params: dict[str, str | int | list[str]] | None = None,
        custom_headers: dict[str, str] | None = None,
    ) -> list[Report]:
        """Get a list of reports from the VTN.

        Parameters
        ----------
        program_id : str | None
            The program ID to filter the reports by.
        event_id : str | None
            The event ID to filter the reports by.
        client_name : str | None
            The client name to filter the reports by.
        skip : int | None
            The number of reports to skip (for pagination).
        limit : int | None
            The maximum number of reports to return.
        extra_params : dict[str, str | int | list[str]] | None
            Extra query parameters to include in the request.
        custom_headers : dict[str, str] | None
            Extra headers to include in the request.

        Returns
        -------
        list[Report]
            A list of report objects.

        Raises
        ------
        ValueError
            If the query parameters are invalid.
        toadr3.ToadrException
            If the request to the VTN fails. Specifically, response status 400, 403, or 500,
        aiohttp.ClientError
            If there is an unexpected error with the HTTP request to the VTN.
        """
        return await toadr3.get_reports(
            session=self._session,
            vtn_url=self._vtn_url,
            access_token=await self.token,
            program_id=program_id,
            event_id=event_id,
            client_name=client_name,
            skip=skip,
            limit=limit,
            extra_params=extra_params,
            custom_headers=custom_headers,
        )

    async def post_report(
        self,
        report: Report,
        custom_headers: dict[str, str] | None = None,
    ) -> Report:
        """Post a report to the VTN.

        Parameters
        ----------
        report : Report
            The report object to post.
        custom_headers : dict[str, str] | None
            Extra headers to include in the request.

        Returns
        -------
        Report
            The report object returned by the VTN.

        Raises
        ------
        ValueError
            If the query parameters are invalid.
        toadr3.ToadrError
            If the request to the VTN fails. Specifically, response status 400, 403, 409, or 500,
        aiohttp.ClientError
            If there is an unexpected error with the HTTP request to the VTN.
        """
        return await toadr3.post_report(
            session=self._session,
            vtn_url=self._vtn_url,
            access_token=await self.token,
            report=report,
            custom_headers=custom_headers,
        )

    async def close(self) -> None:
        """Close the client session."""
        await self._session.close()
        self._closed = True

    async def __aenter__(self) -> Self:
        """Enter async context."""
        if self.closed:
            raise RuntimeError("Client is closed")
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """Exit async context."""
        await self.close()
        return False
