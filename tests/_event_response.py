from _common_test_utils import (
    check_credentials,
    check_custom_header,
    check_extra_params,
    filter_items,
)
from aiohttp import web
from testdata import create_event, create_events


async def events_get_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    if request.headers.get("X-result-type") == "dict":
        # testing header indicating we want to return incorrect result
        sub = create_event()
        return web.json_response(data=sub, status=200)

    credential_response = check_credentials(auth)
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
    extra_param_response = check_extra_params(x_parity)
    if extra_param_response is not None:
        return extra_param_response

    extra_header_response = check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    events = create_events()

    if program_id is not None:
        events = [event for event in events if event["programID"] == program_id]

    if target_type == "RESOURCE_NAME" and target_values is not None:
        events = [event for event in events if event["targets"][0]["values"] == target_values]

    events = filter_items(events, skip, limit, x_parity)

    return web.json_response(data=events)
