import traceback
from collections.abc import Awaitable, Callable

import pytest
from _common_test_utils import create_problem_response
from _event_response import events_get_response
from _programs_response import programs_get_response
from _reports_response import reports_get_response, reports_post_response
from _subscriptions_response import subscriptions_get_response, subscriptions_post_response
from _token_response import token_post_response
from aiohttp import ClientSession, web
from aiohttp.pytest_plugin import AiohttpClient

from toadr3 import AccessToken, OAuthScopeConfig, ToadrClient


async def _exception_wrapper(
    func: Callable[[web.Request], Awaitable[web.Response]],
) -> Callable[[web.Request], Awaitable[web.Response]]:
    """Wrap a function and catch all exceptions.

    Since the web.Application will fail if an exception is raised, this catches these
    exceptions and creates an internal server error (500) instead.
    """

    async def wrapper(request: web.Request) -> web.Response:
        try:
            return await func(request)
        except BaseException as e:  # noqa: BLE001
            return create_problem_response(
                title=f"An unexpected error occurred: {e}",
                status=500,
                detail=(
                    "The MockVTNServer raised an exception instead of "
                    "producing a 'web.Response' object.\n"
                    f"{'*' * 50}\n"
                    "Exception info:\n"
                    f"{''.join(traceback.format_exception(e))}"
                    f"{'*' * 50}\n"
                ),
            )

    return wrapper


@pytest.fixture
async def client(session: ClientSession) -> ToadrClient:
    oauth_config = OAuthScopeConfig(
        token_url="/oauth_url/token_endpoint",
        grant_type="client_credentials",
        scope="test_scope",
        client_id="test_client_id",
        client_secret="test_client_secret",
    )
    return ToadrClient(
        vtn_url="vtn_url",
        oauth_config=oauth_config,
        session=session,
    )


@pytest.fixture
async def session(aiohttp_client: AiohttpClient) -> ClientSession:
    """Create the default client with the default web app."""
    app = web.Application()
    app.router.add_post("/oauth_url/token_endpoint", await _exception_wrapper(token_post_response))
    app.router.add_get("/events", await _exception_wrapper(events_get_response))
    app.router.add_get("/reports", await _exception_wrapper(reports_get_response))
    app.router.add_post("/reports", await _exception_wrapper(reports_post_response))
    app.router.add_get("/programs", await _exception_wrapper(programs_get_response))
    app.router.add_get("/subscriptions", await _exception_wrapper(subscriptions_get_response))
    app.router.add_post("/subscriptions", await _exception_wrapper(subscriptions_post_response))

    return await aiohttp_client(app)  # type: ignore[return-value]


@pytest.fixture
async def token() -> AccessToken:
    return AccessToken("token", 3600)
