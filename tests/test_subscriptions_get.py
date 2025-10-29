import pytest
from aiohttp import ClientSession

from toadr3 import AccessToken, get_subscriptions
from toadr3.models import ObjectType


async def test_get_subscriptions(session: ClientSession, token: AccessToken) -> None:
    subs = await get_subscriptions(session, "vtn_url", token)

    assert len(subs) == 4
    assert {sub.id for sub in subs} == {"2", "3", "4", "7"}


async def test_get_subscriptions_filter_by_objects(
    session: ClientSession, token: AccessToken
) -> None:
    subs = await get_subscriptions(session, "vtn_url", token, objects=[ObjectType.SUBSCRIPTION])
    assert len(subs) == 1

    subs = await get_subscriptions(session, "vtn_url", token, objects=[ObjectType.EVENT])
    assert len(subs) == 3


async def test_get_subscriptions_filter_by_objects_str(
    session: ClientSession, token: AccessToken
) -> None:
    subs = await get_subscriptions(session, "vtn_url", token, objects=["SUBSCRIPTION"])
    assert len(subs) == 1

    subs = await get_subscriptions(session, "vtn_url", token, objects=["EVENT"])
    assert len(subs) == 3


async def test_get_subscriptions_wrong_result_type(
    session: ClientSession, token: AccessToken
) -> None:
    msg = "Expected result to be a list. Got <class 'dict'> instead."
    with pytest.raises(ValueError, match=msg):
        _ = await get_subscriptions(
            session, "vtn_url", token, custom_headers={"X-result-type": "dict"}
        )
