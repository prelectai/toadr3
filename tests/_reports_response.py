from _common_test_utils import (
    check_credentials,
    check_custom_header,
    check_extra_params,
    filter_items,
)
from aiohttp import web
from testdata import create_report, create_reports


async def reports_get_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    if request.headers.get("X-result-type") == "dict":
        # testing header indicating we want to return incorrect result
        sub = create_report()
        return web.json_response(data=sub, status=200)

    credential_response = check_credentials(auth)
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
    extra_param_response = check_extra_params(x_parity)
    if extra_param_response is not None:
        return extra_param_response

    # If custom header is set but not set to "CustomValue" return 400
    extra_header_response = check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    reports = create_reports()

    if program_id is not None:
        reports = [report for report in reports if report["programID"] == program_id]

    if event_id is not None:
        reports = [report for report in reports if report["eventID"] == event_id]

    if client_name is not None:
        reports = [report for report in reports if report["clientName"] == client_name]

    reports = filter_items(reports, skip, limit, x_parity)

    return web.json_response(data=reports)


async def reports_post_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    credential_response = check_credentials(auth)
    if credential_response is not None:
        return credential_response

    # If custom header is set but not set to "CustomValue" return 400
    custom_header = request.headers.get("X-Custom-Header", None)
    extra_header_response = check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    report_data = await request.json()

    if custom_header == "CustomValue":
        report_data["clientName"] = "CustomClientName"

    if report_data["clientName"] == "Unauthorized":
        data = {
            "status": 401,
            "title": "Unauthorized",
            "detail": "You are not authorized to perform this action",
        }
        return web.json_response(data=data, status=401)

    if report_data["eventID"] == "35" or report_data["id"] == "123":
        data = {
            "status": 409,
            "title": "Conflict",
            "detail": "The report already exists",
        }
        return web.json_response(data=data, status=409)

    # Return the report data with some additional fields
    report_data["id"] = "1234"
    report_data["createdDateTime"] = "2024-09-30T12:12:34Z"
    report_data["modificationDateTime"] = "2024-09-30T12:12:35Z"

    return web.json_response(data=report_data)
