import pytest
from aiohttp import ClientSession, web
from aiohttp.pytest_plugin import AiohttpClient
from testdata import create_events

from toadr3 import AccessToken, ToadrError, get_events, models


# ------------------------------------------------------------
# Tests that do not need the event session or a token
# ------------------------------------------------------------
async def test_events_target_type_is_none() -> None:
    msg = "target_type is required when target_values are provided"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, target_values=["121"])  # type: ignore[arg-type]


async def test_events_target_type_is_not_str_or_target_type() -> None:
    msg = "target_type must be TargetType or str"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, target_type=1, target_values=["121"])  # type: ignore[arg-type]


async def test_events_target_values_is_none() -> None:
    msg = "target_values are required when target_type is provided"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, target_type=models.TargetType.SERVICE_AREA)  # type: ignore[arg-type]


async def test_events_target_values_not_list() -> None:
    msg = "target_values must be a list of strings"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(
            None,  # type: ignore[arg-type]
            "",
            None,
            target_type=models.TargetType.SERVICE_AREA,
            target_values="121",  # type: ignore[arg-type]
        )


async def test_events_skip_not_int() -> None:
    msg = "skip must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, skip="0")  # type: ignore[arg-type]


async def test_events_skip_negative() -> None:
    msg = "skip must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, skip=-1)  # type: ignore[arg-type]


async def test_events_limit_not_int() -> None:
    msg = "limit must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, limit="0")  # type: ignore[arg-type]


async def test_events_limit_out_of_range_negative() -> None:
    msg = "limit must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, limit=-1)  # type: ignore[arg-type]


async def test_events_multiple_errors() -> None:
    msg = "target_values are required when target_type is provided, skip must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await get_events(None, "", None, target_type=models.TargetType.SERVICE_AREA, skip=-1)  # type: ignore[arg-type]


# ------------------------------------------------------------
# Tests that need the event session and a token
# ------------------------------------------------------------
async def events_get_response(request: web.Request) -> web.Response:
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
    x_parity = request.query.get("x-parity", None)

    # Check if x-parity is valid here since it is not part of the API
    if x_parity is not None and x_parity not in ["even", "odd"]:
        raise ValueError(f"Invalid value for x-parity: {x_parity}")

    events = create_events()

    if program_id is not None:
        events = [event for event in events if event["programID"] == program_id]

    if target_type == "RESOURCE_NAME" and target_values is not None:
        events = [event for event in events if event["targets"][0]["values"] == target_values]

    if skip is not None:
        int_skip = int(skip)
        events = events[int_skip:]

    if limit is not None:
        int_limit = int(limit)
        events = events[:int_limit]

    if x_parity is not None:
        parity = 0 if x_parity == "even" else 1
        events = [event for event in events if int(event["id"]) % 2 == parity]

    return web.json_response(data=events)


@pytest.fixture
async def session(aiohttp_client: AiohttpClient) -> ClientSession:
    """Create the default client with the default web app."""
    app = web.Application()
    app.router.add_get("/events", events_get_response)
    return await aiohttp_client(app)  # type: ignore[return-value]


@pytest.fixture
async def token() -> AccessToken:
    return AccessToken("token", 3600)


async def test_events_forbidden(session: ClientSession) -> None:
    with pytest.raises(ToadrError) as exc_info:
        _ = await get_events(session, "", None)

    assert exc_info.value.message == "Forbidden"


async def test_events(session: ClientSession, token: AccessToken) -> None:
    events = await get_events(session, "", token)

    assert len(events) == 5
    assert {event.id for event in events} == {"37", "38", "39", "40", "41"}


async def test_events_with_program_id(session: ClientSession, token: AccessToken) -> None:
    events = await get_events(session, "", token, program_id="34")

    assert len(events) == 3
    assert {event.id for event in events} == {"37", "39", "41"}


async def test_events_with_program_id_no_match(session: ClientSession, token: AccessToken) -> None:
    events = await get_events(session, "", token, program_id="31")

    assert len(events) == 0


async def test_events_with_skip(session: ClientSession, token: AccessToken) -> None:
    events = await get_events(session, "", token, skip=1)

    assert len(events) == 4
    assert {event.id for event in events} == {"38", "39", "40", "41"}


async def test_events_with_limit(session: ClientSession, token: AccessToken) -> None:
    events = await get_events(session, "", token, limit=1)

    assert len(events) == 1
    assert {event.id for event in events} == {"37"}


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


async def test_events_with_custom_query_parameters(
    session: ClientSession, token: AccessToken
) -> None:
    reports = await get_events(session, "", token, extra_params={"x-parity": "even"})

    assert len(reports) == 2
    assert {report.id for report in reports} == {"38", "40"}

    reports = await get_events(session, "", token, extra_params={"x-parity": "odd"})
    assert len(reports) == 3
    assert {report.id for report in reports} == {"37", "39", "41"}
