import pytest

import toadr3


async def test_client_context_manager(client: toadr3.ToadrClient) -> None:
    async with client:
        assert await client.token is not None
        assert client.client_session is not None
        assert client.vtn_url == "vtn_url"

    assert client.closed

    with pytest.raises(RuntimeError, match="Client is closed"):
        async with client:
            pass
