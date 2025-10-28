from _common_test_utils import (
    check_credentials,
    check_custom_header,
    check_extra_params,
    filter_items,
)
from aiohttp import web
from testdata import create_program, create_programs


async def programs_get_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    if request.headers.get("X-result-type") == "dict":
        # testing header indicating we want to return incorrect result
        sub = create_program("0", "HB", "Heartbeat")
        return web.json_response(data=sub, status=200)

    credential_response = check_credentials(auth)
    if credential_response is not None:
        return credential_response

    _target_type = request.query.get("targetType", None)
    _target_values = request.query.getall("targetValues", None)
    skip = request.query.get("skip", None)
    limit = request.query.get("limit", None)
    x_parity = request.query.get("x-parity", None)
    custom_header = request.headers.get("X-Custom-Header", None)

    # Check if x-parity is valid here since it is not part of the API
    extra_param_response = check_extra_params(x_parity)
    if extra_param_response is not None:
        return extra_param_response

    # If custom header is set but not set to "CustomValue" return 400
    extra_header_response = check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    programs = create_programs()

    programs = filter_items(programs, skip, limit, x_parity)

    return web.json_response(data=programs, status=200)
