import traceback
from typing import Awaitable, Callable

import pytest
from aiohttp import web
from aiohttp.pytest_plugin import AiohttpClient
from mock_vtn_server import MockVTNServer

from toadr3 import OAuthConfig, ToadrClient


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
            return web.json_response(
                data={
                    "error": f"An unexpected error occurred: {e}",
                    "error_description": "The MockVTNServer raised an exception instead of "
                    "producing a 'web.Response' object.\n"
                    f"{'*' * 50}\n"
                    "Exception info:\n"
                    f"{''.join(traceback.format_exception(e))}"
                    f"{'*' * 50}\n",
                },
                status=500,
            )

    return wrapper


@pytest.fixture
async def client(aiohttp_client: AiohttpClient) -> ToadrClient:
    vtn_server = MockVTNServer()

    app = web.Application()
    app.router.add_post(
        "/oauth_url/token_endpoint", await _exception_wrapper(vtn_server.token_post_response)
    )

    session = await aiohttp_client(app)

    oauth_config = OAuthConfig(
        token_url="/oauth_url/token_endpoint",
        grant_type="client_credentials",
        scope="test_scope",
        client_id="test_client_id",
        client_secret="test_client_secret",
    )
    return ToadrClient(
        vtn_url="vtn_url",
        oauth_config=oauth_config,
        session=session,  # type: ignore
    )
