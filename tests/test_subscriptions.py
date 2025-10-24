from aiohttp import ClientSession

from toadr3 import AccessToken, get_subscriptions
from toadr3.models import ObjectType


async def test_subscriptions(session: ClientSession, token: AccessToken) -> None:
    subs = await get_subscriptions(session, "", token)

    assert len(subs) == 4
    assert {sub.id for sub in subs} == {"2", "3", "4", "7"}


async def test_filter_subscriptions_by_objects(session: ClientSession, token: AccessToken) -> None:
    subs = await get_subscriptions(session, "", token, objects=[ObjectType.SUBSCRIPTION])
    assert len(subs) == 1

    subs = await get_subscriptions(session, "", token, objects=[ObjectType.EVENT])
    assert len(subs) == 3


async def test_filter_subscriptions_by_objects_str(
    session: ClientSession, token: AccessToken
) -> None:
    subs = await get_subscriptions(session, "", token, objects=["SUBSCRIPTION"])
    assert len(subs) == 1

    subs = await get_subscriptions(session, "", token, objects=["EVENT"])
    assert len(subs) == 3
