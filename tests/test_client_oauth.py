import datetime

import pytest

import toadr3


async def test_token(client: toadr3.ToadrClient) -> None:
    token = await client.token

    assert isinstance(token, toadr3.AccessToken)
    assert 0 < token.expires_in <= 3599
    assert token.expires_at is not None
    assert token.token == "test_token"


async def test_token_no_oauth_config(client: toadr3.ToadrClient) -> None:
    new_client = toadr3.ToadrClient(client.vtn_url, None, client.client_session)
    assert await new_client.token is None


async def test_token_expiry(client: toadr3.ToadrClient) -> None:
    token = await client.token
    same_token = await client.token
    assert isinstance(token, toadr3.AccessToken)
    assert isinstance(same_token, toadr3.AccessToken)
    assert token == same_token

    # move expiry timestamp
    assert client._token is not None  # noqa: SLF001
    client._token._expires_at = datetime.datetime.now(tz=datetime.timezone.utc)  # noqa: SLF001
    assert token.is_expired()

    new_token = await client.token
    assert isinstance(new_token, toadr3.AccessToken)
    assert token != new_token


async def test_token_unsupported_grant_type(client: toadr3.ToadrClient) -> None:
    assert client._oauth_config is not None  # noqa: SLF001
    client._oauth_config._grant_type = "custom_grant"  # noqa: SLF001

    with pytest.raises(toadr3.ToadrError, match="unsupported_grant_type") as exc:
        await client.token

    assert exc.value.status_code == 400


async def test_token_scope_error(client: toadr3.ToadrClient) -> None:
    assert client._oauth_config is not None  # noqa: SLF001
    client._oauth_config._claims["scope"] = "wrong_scope"  # noqa: SLF001

    with pytest.raises(toadr3.ToadrError, match="invalid_scope") as exc:
        await client.token

    assert exc.value.status_code == 400


async def test_token_client_id_error(client: toadr3.ToadrClient) -> None:
    assert client._oauth_config is not None  # noqa: SLF001
    client._oauth_config._client_id = "wrong_client_id"  # noqa: SLF001

    with pytest.raises(toadr3.ToadrError, match="unauthorized_client") as exc:
        await client.token

    assert exc.value.status_code == 400


async def test_token_client_secret_error(client: toadr3.ToadrClient) -> None:
    assert client._oauth_config is not None  # noqa: SLF001
    client._oauth_config._client_secret = "wrong_client_secret"  # noqa: SLF001

    with pytest.raises(toadr3.ToadrError, match="invalid_client") as exc:
        await client.token

    assert exc.value.status_code == 401
