import pytest
from aiohttp import ClientSession

from toadr3 import AccessToken, get_reports


async def test_reports(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "vtn_url", token)

    assert len(reports) == 7
    assert {report.id for report in reports} == {"99", "100", "101", "102", "103", "104", "105"}


async def test_reports_with_event_id(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "vtn_url", token, event_id="86")

    assert len(reports) == 1
    assert reports[0].id == "99"


async def test_reports_with_client_name(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "vtn_url", token, client_name="NAC")

    assert len(reports) == 2
    assert {report.id for report in reports} == {"102", "105"}


async def test_reports_extra_query_params_does_not_overwrite(
    session: ClientSession, token: AccessToken
) -> None:
    reports = await get_reports(
        session, "vtn_url", token, program_id="3", extra_params={"programID": "1"}
    )

    assert len(reports) == 3
    assert {report.id for report in reports} == {"103", "104", "105"}


async def test_reports_wrong_result_type(session: ClientSession, token: AccessToken) -> None:
    msg = "Expected result to be a list. Got <class 'dict'> instead."
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(session, "vtn_url", token, custom_headers={"X-result-type": "dict"})
