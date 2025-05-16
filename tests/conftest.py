import pytest
from aiohttp import web
from aiohttp.pytest_plugin import AiohttpClient
from mock_vtn_server import MockVTNServer

from toadr3 import OAuthConfig, ToadrClient


@pytest.fixture
async def client(aiohttp_client: AiohttpClient) -> ToadrClient:
    vtn_server = MockVTNServer()

    app = web.Application()
    app.router.add_post("/oauth_url/token_endpoint", vtn_server.token_post_response)

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
