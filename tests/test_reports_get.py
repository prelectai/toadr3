import pytest
from aiohttp import ClientSession, web
from aiohttp.pytest_plugin import AiohttpClient
from testdata import create_reports

from toadr3 import AccessToken, ToadrError, get_reports


# ------------------------------------------------------------
# Tests that do not need the report session or a token
# ------------------------------------------------------------
async def test_reports_skip_not_int() -> None:
    msg = "skip must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, skip="0")  # type: ignore[arg-type]


async def test_reports_skip_negative() -> None:
    msg = "skip must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, skip=-1)  # type: ignore[arg-type]


async def test_reports_limit_not_int() -> None:
    msg = "limit must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, limit="0")  # type: ignore[arg-type]


async def test_reports_limit_out_of_range_negative() -> None:
    msg = "limit must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, limit=-1)  # type: ignore[arg-type]


async def test_reports_multiple_errors() -> None:
    msg = "skip must be a positive integer, limit must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_reports(None, "", None, skip=-1, limit="9")  # type: ignore[arg-type]


# ------------------------------------------------------------
# Tests that need the report session and a token.
# Mostly the tests checks that the query parameters are
# correctly passed to the request.
# ------------------------------------------------------------
async def reports_get_response(request: web.Request) -> web.Response:
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
    x_parity = request.query.get("x-parity", None)

    # Check if x-parity is valid here since it is not part of the API
    if x_parity is not None and x_parity not in ["even", "odd"]:
        raise ValueError(f"Invalid value for x-parity: {x_parity}")

    reports = create_reports()

    if program_id is not None:
        reports = [report for report in reports if report["programID"] == program_id]

    if event_id is not None:
        reports = [report for report in reports if report["eventID"] == event_id]

    if client_name is not None:
        reports = [report for report in reports if report["clientName"] == client_name]

    if skip is not None:
        reports = reports[int(skip) :]

    if limit is not None:
        reports = reports[: int(limit)]

    if x_parity is not None:
        parity = 0 if x_parity == "even" else 1
        reports = [report for report in reports if int(report["id"]) % 2 == parity]

    return web.json_response(data=reports)


@pytest.fixture
async def session(aiohttp_client: AiohttpClient) -> ClientSession:
    """Create the default client with the default web app."""
    app = web.Application()
    app.router.add_get("/reports", reports_get_response)
    return await aiohttp_client(app)  # type: ignore[return-value]


@pytest.fixture
async def token() -> AccessToken:
    return AccessToken("token", 3600)


async def test_reports_forbidden(session: ClientSession) -> None:
    with pytest.raises(ToadrError) as exc_info:
        _ = await get_reports(session, "", None)

    assert exc_info.value.message == "Forbidden"


async def test_reports(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "", token)

    assert len(reports) == 7
    assert {report.id for report in reports} == {"99", "100", "101", "102", "103", "104", "105"}


async def test_reports_with_program_id(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "", token, program_id="1")

    assert len(reports) == 4
    assert {report.id for report in reports} == {"99", "100", "101", "102"}


async def test_reports_with_event_id(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "", token, event_id="86")

    assert len(reports) == 1
    assert reports[0].id == "99"


async def test_reports_with_client_name(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "", token, client_name="NAC")

    assert len(reports) == 2
    assert {report.id for report in reports} == {"102", "105"}


async def test_reports_with_skip(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "", token, skip=1)

    assert len(reports) == 6
    assert {report.id for report in reports} == {"100", "101", "102", "103", "104", "105"}


async def test_reports_with_limit(session: ClientSession, token: AccessToken) -> None:
    reports = await get_reports(session, "", token, limit=2)

    assert len(reports) == 2
    assert {report.id for report in reports} == {"99", "100"}


async def test_reports_with_extra_query_parameters(
    session: ClientSession, token: AccessToken
) -> None:
    reports = await get_reports(session, "", token, extra_params={"x-parity": "even"})

    assert len(reports) == 3
    assert {report.id for report in reports} == {"100", "102", "104"}

    reports = await get_reports(session, "", token, extra_params={"x-parity": "odd"})
    assert len(reports) == 4
    assert {report.id for report in reports} == {"99", "101", "103", "105"}


async def test_reports_extra_query_params_does_not_overwrite(
    session: ClientSession, token: AccessToken
) -> None:
    reports = await get_reports(session, "", token, program_id="3", extra_params={"programID": "1"})

    assert len(reports) == 3
    assert {report.id for report in reports} == {"103", "104", "105"}
