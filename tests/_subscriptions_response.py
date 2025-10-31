from _common_test_utils import (
    check_credentials,
    check_custom_header,
    check_extra_params,
    filter_items,
)
from aiohttp import web
from testdata import create_subscription, create_subscriptions


async def subscriptions_get_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    if request.headers.get("X-result-type") == "dict":
        # testing header indicating we want to return incorrect result
        sub = create_subscription(sid="13", pid="77")
        return web.json_response(data=sub, status=200)

    credential_response = check_credentials(auth)
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
    extra_param_response = check_extra_params(x_parity)
    if extra_param_response is not None:
        return extra_param_response

    # If custom header is set but not set to "CustomValue" return 400
    extra_header_response = check_custom_header(custom_header)
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

    subs = filter_items(subs, skip, limit, x_parity)

    return web.json_response(data=subs, status=200)


async def subscriptions_post_response(request: web.Request) -> web.Response:
    auth = request.headers.get("Authorization", None)

    if auth is None:
        data = {
            "status": 403,
            "title": "Forbidden",
        }
        return web.json_response(data=data, status=403)

    custom_header = request.headers.get("X-Custom-Header", None)

    extra_header_response = check_custom_header(custom_header)
    if extra_header_response is not None:
        return extra_header_response

    subscription_data = await request.json()

    if custom_header == "CustomValue":
        subscription_data["clientName"] = "CustomClientName"

    if subscription_data["programID"] == "35" or subscription_data["id"] == "123":
        data = {
            "status": 409,
            "title": "Conflict",
            "detail": "The subscription already exists",
        }
        return web.json_response(data=data, status=409)

    # Return the report data with some additional fields
    subscription_data["id"] = "123"
    subscription_data["createdDateTime"] = "2024-09-30T12:12:34Z"
    subscription_data["modificationDateTime"] = "2024-09-30T12:12:35Z"

    return web.json_response(data=subscription_data)
