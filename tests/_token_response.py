from aiohttp import web


async def token_post_response(request: web.Request) -> web.Response:
    """Handle the token post request."""
    data = await request.post()
    grant_type = str(data.get("grant_type"))
    client_id = str(data.get("client_id"))
    client_secret = str(data.get("client_secret"))
    scope = str(data.get("scope"))

    result: dict[str, str | int | None] = {
        "error": None,
        "error_description": "",
        "error_uri": "",
    }
    # https://www.rfc-editor.org/rfc/rfc6749#section-5.2
    # invalid_request and invalid_grant are not tested here (yet)
    match grant_type, client_id, client_secret, scope:
        case ("client_credentials", "test_client_id", "test_client_secret", "test_scope"):
            # correct query
            result = {
                "token_type": "Bearer",
                "expires_in": 3599,
                "access_token": "test_token",
            }
            status = 200
        case ("custom_grant", "test_client_id", "test_client_secret", "test_scope"):
            # unsupported grant type
            result["error"] = "unsupported_grant_type"
            status = 400
        case ("client_credentials", "test_client_id", "test_client_secret", "wrong_scope"):
            # wrong scope
            result["error"] = "invalid_scope"
            status = 400
        case ("client_credentials", "wrong_client_id", "test_client_secret", "test_scope"):
            # wrong client id
            result["error"] = "unauthorized_client"
            status = 400
        case ("client_credentials", "test_client_id", "wrong_client_secret", "test_scope"):
            # invalid client secret
            result["error"] = "invalid_client"
            status = 401
        case _:
            # unknown error
            status = 500
            result["error"] = "internal_server_error"
            result["error_description"] = (
                "No handling implemented for this combination "
                f"of parameters: '{grant_type}' '{client_id}' '{client_secret}' '{scope}'"
            )
    return web.json_response(data=result, status=status)
