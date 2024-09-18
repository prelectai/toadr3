import pytest
from aiohttp import ClientSession, web
from aiohttp.pytest_plugin import AiohttpClient
from testdata import create_event

from toadr3 import AccessToken, TargetType, ToadrError, get_events


# ------------------------------------------------------------
# Tests that do not need the event session or a token
# ------------------------------------------------------------
async def test_events_target_type_is_none():
    msg = "target_type is required when target_values are provided"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, target_values=["121"])


async def test_events_target_values_is_none():
    msg = "target_values are required when target_type is provided"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, target_type=TargetType.SERVICE_AREA)


async def test_events_target_values_not_list():
    msg = "target_values must be a list of strings"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(
            None, "", None, target_type=TargetType.SERVICE_AREA, target_values="121"
        )


async def test_events_skip_not_int():
    msg = "skip must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, skip="0")


async def test_events_skip_negative():
    msg = "skip must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, skip=-1)


async def test_events_limit_not_int():
    msg = "limit must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, limit="0")


async def test_events_limit_out_of_range_negative():
    msg = "limit must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, limit=-1)


# ------------------------------------------------------------
# Tests that need the event session and a token
# ------------------------------------------------------------
async def events_response_get(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    if auth is None:
        data = {
            "status": 403,
            "title": "Forbidden",
        }
        return web.json_response(data=data, status=403)

    program_id = request.query.get("programID", None)
    target_type = request.query.get("targetType", None)
    target_values = request.query.getall("targetValues", None)
    skip = request.query.get("skip", None)
    limit = request.query.get("limit", None)

    if skip is not None:
        skip = int(skip)

    if limit is not None:
        limit = int(limit)

    match program_id, target_type, target_values, skip, limit:
        case (None, None, None, None, None):
            # No query parameters -> all events
            data = [create_event(programID="42"), create_event(programID="69")]
            return web.json_response(data=data)

        case ("42", None, None, None, None):
            # programID=42 -> one match
            data = [create_event(programID="42")]
            return web.json_response(data=data)

        case ("31", None, None, None, None):
            # programID=31 -> no matches
            data = []
            return web.json_response(data=data)

        case (None, None, None, 1, None):
            # skip=1 -> skip the first match
            data = [create_event(programID="69")]
            return web.json_response(data=data)

        case (None, None, None, None, 1):
            # limit=1 -> only the first match
            data = [create_event(programID="42")]
            return web.json_response(data=data)

        case (None, "RESOURCE_NAME", ["121"], None, None):
            # target_type=RESOURCE_NAME, target_values=["121"] -> all events
            data = [create_event(programID="42"), create_event(programID="69")]
            return web.json_response(data=data)

        case _:
            raise ValueError(f"Unexpected query parameters: {request.query}")


@pytest.fixture
async def events_session(aiohttp_client: AiohttpClient) -> ClientSession:
    """Create the default client with the default web app."""
    app = web.Application()
    app.router.add_get("/events", events_response_get)
    client = await aiohttp_client(app)
    return client


@pytest.fixture
async def token() -> AccessToken:
    return AccessToken("token", 3600)


async def test_events_forbidden(events_session: ClientSession):
    with pytest.raises(ToadrError) as exc_info:
        _ = await get_events(events_session, "", None)

    assert exc_info.value.message == "Forbidden"


async def test_events(events_session: ClientSession, token: AccessToken):
    events = await get_events(events_session, "", token)

    assert len(events) == 2
    assert {event.program_id for event in events} == {"42", "69"}


async def test_events_with_program_id(events_session: ClientSession, token: AccessToken):
    events = await get_events(events_session, "", token, program_id="42")

    assert len(events) == 1
    assert events[0].program_id == "42"


async def test_events_with_program_id_no_match(events_session: ClientSession, token: AccessToken):
    events = await get_events(events_session, "", token, program_id="31")

    assert len(events) == 0


async def test_events_with_skip(events_session: ClientSession, token: AccessToken):
    events = await get_events(events_session, "", token, skip=1)

    assert len(events) == 1
    assert events[0].program_id == "69"


async def test_events_with_limit(events_session: ClientSession, token: AccessToken):
    events = await get_events(events_session, "", token, limit=1)

    assert len(events) == 1
    assert events[0].program_id == "42"


async def test_events_with_target_values(events_session: ClientSession, token: AccessToken):
    events = await get_events(
        events_session, "", token, target_type=TargetType.RESOURCE_NAME, target_values=["121"]
    )

    assert len(events) == 2
    assert {event.program_id for event in events} == {"42", "69"}
