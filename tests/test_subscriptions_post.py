import datetime

import pytest
from testdata import create_subscription

from toadr3 import ToadrClient, ToadrError, post_subscription
from toadr3.models import Subscription


async def test_post_subscription_forbidden(client: ToadrClient) -> None:
    mock_client = ToadrClient(client.vtn_url, None, client.client_session)
    session = mock_client.client_session
    token = await mock_client.token
    vtn_url = mock_client.vtn_url

    subscription = Subscription.model_validate(create_subscription(sid="6", pid="77"))

    msg = "Forbidden"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_subscription(session, vtn_url, token, subscription)

    with pytest.raises(ToadrError, match=msg):
        await getattr(mock_client, post_subscription.__name__)(subscription)


async def test_post_subscription_conflict(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    data = create_subscription(sid="123", pid="35")
    subscription = Subscription.model_validate(data)

    msg = "Conflict - The subscription already exists"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_subscription(session, vtn_url, token, subscription)

    with pytest.raises(ToadrError, match=msg):
        await client.post_subscription(subscription)


async def test_post_subscription(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    subscription = Subscription.model_validate(create_subscription(sid="6", pid="77"))
    result = await post_subscription(session, vtn_url, token, subscription)

    assert result.id == "123"
    assert result.client_name == "YAC"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")

    result = await client.post_subscription(subscription)
    assert result.id == "123"
    assert result.client_name == "YAC"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")


async def test_post_subscription_custom_header(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    subscription = Subscription.model_validate(create_subscription(sid="6", pid="77"))
    result = await post_subscription(
        session, vtn_url, token, subscription, custom_headers={"X-Custom-Header": "CustomValue"}
    )
    assert result.id == "123"
    assert result.client_name == "CustomClientName"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")

    result = await client.post_subscription(
        subscription, custom_headers={"X-Custom-Header": "CustomValue"}
    )
    assert result.id == "123"
    assert result.client_name == "CustomClientName"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")


async def test_post_subscription_invalid_custom_header(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    subscription = Subscription.model_validate(create_subscription(sid="6", pid="77"))

    msg = "Bad Request - Invalid value for X-Custom-Header: InvalidValue"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_subscription(
            session,
            vtn_url,
            token,
            subscription,
            custom_headers={"X-Custom-Header": "InvalidValue"},
        )

    with pytest.raises(ToadrError, match=msg):
        _ = await client.post_subscription(
            subscription, custom_headers={"X-Custom-Header": "InvalidValue"}
        )


async def test_post_subscription_is_none(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    msg = "subscription is required"
    with pytest.raises(ValueError, match=msg):
        _ = await post_subscription(None, "vtn_url", None, None)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=msg):
        _ = await post_subscription(session, vtn_url, token, None)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=msg):
        _ = await client.post_subscription(None)  # type: ignore[arg-type]
