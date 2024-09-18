import pytest
from aiohttp import web
from aiohttp.pytest_plugin import AiohttpClient

from toadr3 import AccessToken, ToadrError, acquire_access_token


def test_valid_access_token():
    token = AccessToken("123", 3600)
    assert token.token == "123"
    assert token.expires_in <= 3600
    assert token.is_expired() is False
    assert str(token) == "123"
    assert repr(token).startswith("AccessToken(token='123', expires_in=")


def test_expired_access_token():
    token = AccessToken("123", 59)
    assert token.token == "123"
    assert 0 < token.expires_in <= 59
    assert token.is_expired() is True


async def test_acquire_access_token_none_scope():
    with pytest.raises(ValueError, match="scope is required"):
        _ = await acquire_access_token(
            None, "url", "grant_type", None, "client_id", "client_secret"
        )


async def test_acquire_access_token_none_grant_type():
    with pytest.raises(ValueError, match="grant_type is required"):
        _ = await acquire_access_token(None, "url", None, "scope", "client_id", "client_secret")


async def test_acquire_access_token_missing_client_id(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CLIENT_ID", raising=False)
    with pytest.raises(ValueError, match="client_id is required"):
        _ = await acquire_access_token(None, "url", "grant_type", "scope", None, "client_secret")


async def test_acquire_access_token_missing_client_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CLIENT_SECRET", raising=False)
    with pytest.raises(ValueError, match="client_secret is required"):
        _ = await acquire_access_token(None, "url", "grant_type", "scope", "client_id", None)


async def test_acquire_access_token_client_id_and_secret_from_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CLIENT_ID", "env_id")
    monkeypatch.setenv("CLIENT_SECRET", "env_secret")

    # check that the error message is about the missing grant_type
    # and not client_id or client_secret
    with pytest.raises(ValueError, match="grant_type is required"):
        _ = await acquire_access_token(None, "url", None, None)


async def token_response(request: web.Request) -> web.Response:
    if request.method == "POST":
        data = await request.post()
        grant_type = data.get("grant_type")
        client_id = data.get("client_id")
        client_secret = data.get("client_secret")
        scope = data.get("scope")
        # https://www.rfc-editor.org/rfc/rfc6749#section-5.2
        # invalid_request and invalid_grant are not tested here (yet)
        match grant_type, client_id, client_secret, scope:
            case ("client_credentials", "client_id", "client_secret", "scope"):
                # correct query
                data = {
                    "token_type": "Bearer",
                    "expires_in": 3599,
                    "access_token": "123",
                }
                return web.json_response(data=data, status=200)
            case ("wrong_credentials", "client_id", "client_secret", "scope"):
                # unsupported grant type
                data = {
                    "error": "unsupported_grant_type",
                    "error_description": "",
                    "error_uri": "",
                }
                return web.json_response(data=data, status=400)
            case ("client_credentials", "client_id", "client_secret", "wrong_scope"):
                # wrong scope
                data = {
                    "error": "invalid_scope",
                    "error_description": "",
                    "error_uri": "",
                }
                return web.json_response(data=data, status=400)
            case ("client_credentials", "wrong_client_id", "client_secret", "scope"):
                # wrong client id
                data = {
                    "error": "unauthorized_client",
                    "error_description": "",
                    "error_uri": "",
                }
                return web.json_response(data=data, status=400)
            case ("client_credentials", "client_id", "wrong_client_secret", "scope"):
                # invalid client secret
                data = {
                    "error": "invalid_client",
                    "error_description": "",
                    "error_uri": "",
                }
                return web.json_response(data=data, status=401)
            case _:
                # unknown error
                pytest.fail(f"Unknown query: {grant_type}, {client_id}, {client_secret}, {scope}")
    raise UserWarning(f"Invalid request method: {request.method}")


async def test_acquire_access_token(aiohttp_client: AiohttpClient):
    app = web.Application()
    app.router.add_post("/token", token_response)
    client = await aiohttp_client(app)

    access_token = await acquire_access_token(
        client, "/token", "client_credentials", "scope", "client_id", "client_secret"
    )

    assert access_token.token == "123"
    assert access_token.expires_in < 3600
    assert access_token.expires_in > 0
    assert access_token.is_expired() is False


async def check_acquire_access_token_error(
    aiohttp_client: AiohttpClient,
    grant_type: str,
    scope: str,
    client_id: str,
    client_secret: str,
    expected_status: int,
    expected_error: str,
):
    """Check that the acquire_access_token function raises the expected error."""
    app = web.Application()
    app.router.add_post("/token", token_response)
    client = await aiohttp_client(app)

    with pytest.raises(ToadrError) as e:
        await acquire_access_token(client, "/token", grant_type, scope, client_id, client_secret)

    err: ToadrError = e.value
    assert err.message == "Failed to acquire access token"
    assert err.status_code == expected_status
    assert err.json_response["error"] == expected_error


@pytest.mark.asyncio
async def test_acquire_access_token_grant_type_error(aiohttp_client: AiohttpClient):
    await check_acquire_access_token_error(
        aiohttp_client,
        grant_type="wrong_credentials",
        scope="scope",
        client_id="client_id",
        client_secret="client_secret",
        expected_status=400,
        expected_error="unsupported_grant_type",
    )


@pytest.mark.asyncio
async def test_acquire_access_token_scope_error(aiohttp_client: AiohttpClient):
    await check_acquire_access_token_error(
        aiohttp_client,
        grant_type="client_credentials",
        scope="wrong_scope",
        client_id="client_id",
        client_secret="client_secret",
        expected_status=400,
        expected_error="invalid_scope",
    )


@pytest.mark.asyncio
async def test_acquire_access_token_client_id_error(aiohttp_client: AiohttpClient):
    await check_acquire_access_token_error(
        aiohttp_client,
        grant_type="client_credentials",
        scope="scope",
        client_id="wrong_client_id",
        client_secret="client_secret",
        expected_status=400,
        expected_error="unauthorized_client",
    )


@pytest.mark.asyncio
async def test_acquire_access_token_client_secret_error(aiohttp_client: AiohttpClient):
    await check_acquire_access_token_error(
        aiohttp_client,
        grant_type="client_credentials",
        scope="scope",
        client_id="client_id",
        client_secret="wrong_client_secret",
        expected_status=401,
        expected_error="invalid_client",
    )
