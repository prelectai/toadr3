import traceback
from collections.abc import Awaitable, Callable

import pytest
from aiohttp import ClientSession, web
from aiohttp.pytest_plugin import AiohttpClient
from mock_vtn_server import MockVTNServer
from testdata import create_events, create_programs, create_reports, create_subscriptions

from toadr3 import AccessToken, OAuthScopeConfig, ToadrClient
from toadr3.models import Problem


def create_problem_response(title: str, status: int, detail: str) -> web.Response:
    """Create a web.Response with a Problem JSON body."""
    return web.json_response(
        data=Problem(
            title=title,
            status=status,
            detail=detail,
        ),
        status=status,
        dumps=Problem.model_dump_json,
    )


async def _exception_wrapper(
    func: Callable[[web.Request], Awaitable[web.Response]],
) -> Callable[[web.Request], Awaitable[web.Response]]:
    """Wrap a function and catch all exceptions.

    Since the web.Application will fail if an exception is raised, this catches these
    exceptions and creates an internal server error (500) instead.
    """

    async def wrapper(request: web.Request) -> web.Response:
        try:
            return await func(request)
        except BaseException as e:  # noqa: BLE001
            return create_problem_response(
                title=f"An unexpected error occurred: {e}",
                status=500,
                detail=(
                    "The MockVTNServer raised an exception instead of "
                    "producing a 'web.Response' object.\n"
                    f"{'*' * 50}\n"
                    "Exception info:\n"
                    f"{''.join(traceback.format_exception(e))}"
                    f"{'*' * 50}\n"
                ),
            )

    return wrapper


@pytest.fixture
async def client(aiohttp_client: AiohttpClient) -> ToadrClient:
    vtn_server = MockVTNServer()

    app = web.Application()
    app.router.add_post(
        "/oauth_url/token_endpoint", await _exception_wrapper(vtn_server.token_post_response)
    )

    session = await aiohttp_client(app)

    oauth_config = OAuthScopeConfig(
        token_url="/oauth_url/token_endpoint",
        grant_type="client_credentials",
        scope="test_scope",
        client_id="test_client_id",
        client_secret="test_client_secret",
    )
    return ToadrClient(
        vtn_url="vtn_url",
        oauth_config=oauth_config,
        session=session,  # type: ignore
    )


def _check_extra_params(x_parity: str | None) -> web.Response | None:
    """Check if the x-parity parameter is valid."""
    if x_parity is not None and x_parity not in ["even", "odd"]:
        return create_problem_response(
            title="Bad Request",
            status=400,
            detail=f"Invalid value for x-parity: {x_parity}",
        )
    return None


def _check_custom_header(custom_header: str | None) -> web.Response | None:
    """Check if the custom header is valid."""
    if custom_header is not None and custom_header != "CustomValue":
        return create_problem_response(
            title="Bad Request",
            status=400,
            detail=f"Invalid value for X-Custom-Header: {custom_header}",
        )
    return None


def _check_credentials(auth: str | None) -> web.Response | None:
    """Check if the credentials are valid."""
    if auth is None or not auth.startswith("Bearer ") or auth.split(" ")[1] != "token":
        return create_problem_response(
            title="Forbidden",
            status=403,
            detail="Invalid or missing access token",
        )
    return None


def _filter(
    items: list[dict[str, str]], skip: str | None, limit: str | None, x_parity: str | None
) -> list[dict[str, str]]:
    """Filter the items based on skip, limit and x_parity parameters."""
    if skip is not None:
        int_skip = int(skip)
        items = items[int_skip:]

    if limit is not None:
        int_limit = int(limit)
        items = items[:int_limit]

    if x_parity is not None:
        parity = 0 if x_parity == "even" else 1
        items = [item for item in items if int(item["id"]) % 2 == parity]

    return items


async def _events_get_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    credential_response = _check_credentials(auth)
    if credential_response is not None:
        return credential_response

    program_id = request.query.get("programID", None)
    target_type = request.query.get("targetType", None)
    target_values = request.query.getall("targetValues", None)
    skip = request.query.get("skip", None)
    limit = request.query.get("limit", None)
    x_parity = request.query.get("x-parity", None)
    custom_header = request.headers.get("X-Custom-Header", None)

    # Check if x-parity is valid here since it is not part of the API
    extra_param_response = _check_extra_params(x_parity)
    if extra_param_response is not None:
        return extra_param_response

    extra_header_response = _check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    events = create_events()

    if program_id is not None:
        events = [event for event in events if event["programID"] == program_id]

    if target_type == "RESOURCE_NAME" and target_values is not None:
        events = [event for event in events if event["targets"][0]["values"] == target_values]

    events = _filter(events, skip, limit, x_parity)

    return web.json_response(data=events)


async def _reports_get_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    credential_response = _check_credentials(auth)
    if credential_response is not None:
        return credential_response

    program_id = request.query.get("programID", None)
    event_id = request.query.get("eventID", None)
    client_name = request.query.get("clientName", None)
    skip = request.query.get("skip", None)
    limit = request.query.get("limit", None)
    x_parity = request.query.get("x-parity", None)
    custom_header = request.headers.get("X-Custom-Header", None)

    # Check if x-parity is valid here since it is not part of the API
    extra_param_response = _check_extra_params(x_parity)
    if extra_param_response is not None:
        return extra_param_response

    # If custom header is set but not set to "CustomValue" return 400
    extra_header_response = _check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    reports = create_reports()

    if program_id is not None:
        reports = [report for report in reports if report["programID"] == program_id]

    if event_id is not None:
        reports = [report for report in reports if report["eventID"] == event_id]

    if client_name is not None:
        reports = [report for report in reports if report["clientName"] == client_name]

    reports = _filter(reports, skip, limit, x_parity)

    return web.json_response(data=reports)


async def _programs_get_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    credential_response = _check_credentials(auth)
    if credential_response is not None:
        return credential_response

    _target_type = request.query.get("targetType", None)
    _target_values = request.query.getall("targetValues", None)
    skip = request.query.get("skip", None)
    limit = request.query.get("limit", None)
    x_parity = request.query.get("x-parity", None)
    custom_header = request.headers.get("X-Custom-Header", None)

    # Check if x-parity is valid here since it is not part of the API
    extra_param_response = _check_extra_params(x_parity)
    if extra_param_response is not None:
        return extra_param_response

    # If custom header is set but not set to "CustomValue" return 400
    extra_header_response = _check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    programs = create_programs()

    programs = _filter(programs, skip, limit, x_parity)

    return web.json_response(data=programs, status=200)


async def _subscriptions_get_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    credential_response = _check_credentials(auth)
    if credential_response is not None:
        return credential_response

    program_id = request.query.get("programID", None)
    client_name = request.query.get("clientName", None)
    _target_type = request.query.get("targetType", None)
    _target_values = request.query.getall("targetValues", None)
    objects = request.query.getall("objects", None)
    skip = request.query.get("skip", None)
    limit = request.query.get("limit", None)
    x_parity = request.query.get("x-parity", None)
    custom_header = request.headers.get("X-Custom-Header", None)

    # Check if x-parity is valid here since it is not part of the API
    extra_param_response = _check_extra_params(x_parity)
    if extra_param_response is not None:
        return extra_param_response

    # If custom header is set but not set to "CustomValue" return 400
    extra_header_response = _check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    subs = create_subscriptions()

    if program_id is not None:
        subs = [sub for sub in subs if sub["programID"] == program_id]

    if client_name is not None:
        subs = [sub for sub in subs if sub["clientName"] == client_name]

    if objects is not None:
        result = []
        for sub in subs:
            object_names = set()
            for obj_op in sub["objectOperations"]:
                for object_name in obj_op["objects"]:
                    object_names.add(object_name)

            if any(object_name in object_names for object_name in objects):
                result.append(sub)

        subs = result

    subs = _filter(subs, skip, limit, x_parity)

    return web.json_response(data=subs, status=200)


@pytest.fixture
async def session(aiohttp_client: AiohttpClient) -> ClientSession:
    """Create the default client with the default web app."""
    app = web.Application()
    app.router.add_get("/events", await _exception_wrapper(_events_get_response))
    app.router.add_get("/reports", await _exception_wrapper(_reports_get_response))
    app.router.add_get("/programs", await _exception_wrapper(_programs_get_response))
    app.router.add_get("/subscriptions", await _exception_wrapper(_subscriptions_get_response))

    return await aiohttp_client(app)  # type: ignore[return-value]


@pytest.fixture
async def token() -> AccessToken:
    return AccessToken("token", 3600)
