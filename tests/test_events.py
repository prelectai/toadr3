import pytest
from aiohttp import ClientSession

from toadr3 import AccessToken, get_events, models


async def test_events(session: ClientSession, token: AccessToken) -> None:
    events = await get_events(session, "", token)

    assert len(events) == 5
    assert {event.id for event in events} == {"37", "38", "39", "40", "41"}


async def test_events_with_target_values(session: ClientSession, token: AccessToken) -> None:
    events = await get_events(
        session, "", token, target_type=models.TargetType.RESOURCE_NAME, target_values=["1211"]
    )

    assert len(events) == 2
    assert {event.program_id for event in events} == {"34", "35"}


async def test_events_with_target_values_and_str_target_type(
    session: ClientSession, token: AccessToken
) -> None:
    events = await get_events(
        session, "", token, target_type="RESOURCE_NAME", target_values=["1211"]
    )

    assert len(events) == 2
    assert {event.program_id for event in events} == {"34", "35"}


async def test_events_wrong_result_type(session: ClientSession, token: AccessToken) -> None:
    msg = "Expected result to be a list. Got <class 'dict'> instead."
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(session, "", token, custom_headers={"X-result-type": "dict"})
