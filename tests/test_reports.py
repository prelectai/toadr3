import pytest
from aiohttp import ClientSession, web
from aiohttp.pytest_plugin import AiohttpClient
from testdata import create_reports

from toadr3 import AccessToken, ToadrError, get_reports


# ------------------------------------------------------------
# Tests that do not need the report session or a token
# ------------------------------------------------------------
async def test_reports_skip_not_int():
    msg = "skip must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, skip="0")


async def test_reports_skip_negative():
    msg = "skip must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, skip=-1)


async def test_reports_limit_not_int():
    msg = "limit must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, limit="0")


async def test_reports_limit_out_of_range_negative():
    msg = "limit must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, limit=-1)


# ------------------------------------------------------------
# Tests that need the report session and a token.
# Mostly the tests checks that the query parameters are
# correctly passed to the request.
# ------------------------------------------------------------
async def reports_response_get(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    if auth is None:
        data = {
            "status": 403,
            "title": "Forbidden",
        }
        return web.json_response(data=data, status=403)

    program_id = request.query.get("programID", None)
    event_id = request.query.get("eventID", None)
    client_name = request.query.get("clientName", None)
    skip = request.query.get("skip", None)
    limit = request.query.get("limit", None)

    if skip is not None:
        skip = int(skip)

    if limit is not None:
        limit = int(limit)

    reports = create_reports()
    match program_id, event_id, client_name, skip, limit:
        case None, None, None, None, None:
            return web.json_response(data=reports)
        case pid, None, None, None, None:
            data = [report for report in reports if report["programID"] == pid]
            return web.json_response(data=data)
        case None, eid, None, None, None:
            data = [report for report in reports if report["eventID"] == eid]
            return web.json_response(data=data)
        case None, None, cname, None, None:
            data = [report for report in reports if report["clientName"] == cname]
            return web.json_response(data=data)
        case None, None, None, skp, None:
            return web.json_response(data=reports[skp:])
        case None, None, None, None, lmt:
            return web.json_response(data=reports[:lmt])
        case _:
            raise ValueError(f"Unexpected query parameters: {request.query}")


@pytest.fixture
async def session(aiohttp_client: AiohttpClient) -> ClientSession:
    """Create the default client with the default web app."""
    app = web.Application()
    app.router.add_get("/reports", reports_response_get)
    return await aiohttp_client(app)


@pytest.fixture
async def token() -> AccessToken:
    return AccessToken("token", 3600)


async def test_reports_forbidden(session: ClientSession):
    with pytest.raises(ToadrError) as exc_info:
        _ = await get_reports(session, "", None)

    assert exc_info.value.message == "Forbidden"


async def test_reports(session: ClientSession, token: AccessToken):
    reports = await get_reports(session, "", token)

    assert len(reports) == 7
    assert {report.id for report in reports} == {"99", "100", "101", "102", "103", "104", "105"}


async def test_reports_with_program_id(session: ClientSession, token: AccessToken):
    reports = await get_reports(session, "", token, program_id="1")

    assert len(reports) == 4
    assert {report.id for report in reports} == {"99", "100", "101", "102"}


async def test_reports_with_event_id(session: ClientSession, token: AccessToken):
    reports = await get_reports(session, "", token, event_id="86")

    assert len(reports) == 1
    assert reports[0].id == "99"


async def test_reports_with_client_name(session: ClientSession, token: AccessToken):
    reports = await get_reports(session, "", token, client_name="NAC")

    assert len(reports) == 2
    assert {report.id for report in reports} == {"102", "105"}


async def test_reports_with_skip(session: ClientSession, token: AccessToken):
    reports = await get_reports(session, "", token, skip=1)

    assert len(reports) == 6
    assert {report.id for report in reports} == {"100", "101", "102", "103", "104", "105"}


async def test_reports_with_limit(session: ClientSession, token: AccessToken):
    reports = await get_reports(session, "", token, limit=2)

    assert len(reports) == 2
    assert {report.id for report in reports} == {"99", "100"}
