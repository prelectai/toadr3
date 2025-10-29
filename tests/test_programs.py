import pytest
from aiohttp import ClientSession

from toadr3 import AccessToken, get_programs


async def test_programs(session: ClientSession, token: AccessToken) -> None:
    programs = await get_programs(session, "vtn_url", token)

    assert len(programs) == 3
    assert {program.id for program in programs} == {"0", "1", "2"}


async def test_programs_wrong_result_type(session: ClientSession, token: AccessToken) -> None:
    msg = "Expected result to be a list. Got <class 'dict'> instead."
    with pytest.raises(ValueError, match=msg):
        _ = await get_programs(session, "vtn_url", token, custom_headers={"X-result-type": "dict"})
