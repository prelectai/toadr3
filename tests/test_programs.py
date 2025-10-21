from aiohttp import ClientSession

from toadr3 import AccessToken, get_programs


async def test_programs(session: ClientSession, token: AccessToken) -> None:
    programs = await get_programs(session, "", token)

    assert len(programs) == 3
    assert {program.id for program in programs} == {"0", "1", "2"}
