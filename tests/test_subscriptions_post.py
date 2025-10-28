import datetime

import pytest
from aiohttp import ClientSession
from testdata import create_subscription

from toadr3 import AccessToken, ToadrError, post_subscription
from toadr3.models import Subscription


async def test_post_subscription_required() -> None:
    msg = "subscription is required"
    with pytest.raises(ValueError, match=msg):
        _ = await post_subscription(None, "", None, None)  # type: ignore[arg-type]


async def test_post_subscription_forbidden(session: ClientSession) -> None:
    report = Subscription.model_validate(create_subscription(sid="6", pid="77"))
    with pytest.raises(ToadrError) as exc_info:
        _ = await post_subscription(session, "", None, report)

    assert exc_info.value.message == "Forbidden"


async def test_post_subscription_conflict(session: ClientSession, token: AccessToken) -> None:
    data = create_subscription(sid="123", pid="35")
    report = Subscription.model_validate(data)

    msg = "Conflict - The subscription already exists"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_subscription(session, "", token, report)


async def test_post_subscription(session: ClientSession, token: AccessToken) -> None:
    report = Subscription.model_validate(create_subscription(sid="6", pid="77"))
    result = await post_subscription(session, "", token, report)

    assert result.id == "123"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")


async def test_post_subscription_custom_header(session: ClientSession, token: AccessToken) -> None:
    report = Subscription.model_validate(create_subscription(sid="6", pid="77"))
    result = await post_subscription(
        session, "", token, report, custom_headers={"X-Custom-Header": "CustomValue"}
    )

    assert result.id == "123"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")


async def test_post_subscription_invalid_custom_header(
    session: ClientSession, token: AccessToken
) -> None:
    report = Subscription.model_validate(create_subscription(sid="6", pid="77"))

    msg = "Bad Request - Invalid value for X-Custom-Header: InvalidValue"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_subscription(
            session, "", token, report, custom_headers={"X-Custom-Header": "InvalidValue"}
        )


async def test_post_subscription_is_none(session: ClientSession, token: AccessToken) -> None:
    with pytest.raises(ValueError, match="subscription is required"):
        _ = await post_subscription(session, "", token, None)  # type: ignore[arg-type]
