import datetime

import pytest
from aiohttp import ClientSession, web
from aiohttp.pytest_plugin import AiohttpClient
from testdata import create_report

from toadr3 import AccessToken, Report, ToadrError, post_report, toadr_json_serialize


async def test_post_report_required():
    msg = "report is required"
    with pytest.raises(ValueError, match=msg):
        _ = await post_report(None, "", None, None)


# ------------------------------------------------------------
# Tests that need the report session and a token.
# Mostly the tests checks that the query parameters are
# correctly passed to the request.
# ------------------------------------------------------------
async def reports_post_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    if auth is None:
        data = {
            "status": 403,
            "title": "Forbidden",
        }
        return web.json_response(data=data, status=403)

    report_data = await request.json()

    if report_data["eventID"] == "35" or report_data["id"] == "123":
        data = {
            "status": 409,
            "title": "Conflict",
            "detail": "The report already exists",
        }
        return web.json_response(data=data, status=409)

    # Return the report data with some additional fields
    report_data["id"] = "123"
    report_data["createdDateTime"] = "2024-09-30T12:12:34Z"
    report_data["modificationDateTime"] = "2024-09-30T12:12:35Z"

    return web.json_response(data=report_data)


@pytest.fixture
async def session(aiohttp_client: AiohttpClient) -> ClientSession:
    """Create the default client with the default web app."""
    app = web.Application()
    app.router.add_post("/reports", reports_post_response)
    return await aiohttp_client(app, json_serialize=toadr_json_serialize)


@pytest.fixture
async def token() -> AccessToken:
    return AccessToken("token", 3600)


async def test_post_report_forbidden(session: ClientSession):
    report = Report(create_report())
    with pytest.raises(ToadrError) as exc_info:
        _ = await post_report(session, "", None, report)

    assert exc_info.value.message == "Forbidden"


async def test_post_report_conflict(session: ClientSession, token: AccessToken):
    data = create_report()
    data["eventID"] = "35"
    report = Report(data)

    msg = "Conflict - The report already exists"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_report(session, "", token, report)


async def test_post_report(session: ClientSession, token: AccessToken):
    report = Report(create_report())
    result = await post_report(session, "", token, report)

    assert result.id == "123"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")
