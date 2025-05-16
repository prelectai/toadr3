from aiohttp import web


class MockVTNServer:
    """Mock a VTN server for testing."""

    def __init__(self) -> None:
        self._scope = "test_scope"
        self._grant_type = "client_credentials"
        self._client_id = "test_client_id"
        self._client_secret = "test_client_secret"
        self._token = "test_token"

    def _check_auth(self, request: web.Request, token: str) -> web.Response | None:
        auth = request.headers.get("Authorization", None)

        if auth is None:
            data = {
                "status": 403,
                "title": "Forbidden",
            }
            return web.json_response(data=data, status=403)

        if auth != f"Bearer {token}":
            data = {
                "status": 401,
                "title": "Unauthorized",
            }
            return web.json_response(data=data, status=401)
        return None

    async def token_post_response(self, request: web.Request) -> web.Response:
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
            case (self._grant_type, self._client_id, self._client_secret, self._scope):
                # correct query
                result = {
                    "token_type": "Bearer",
                    "expires_in": 3599,
                    "access_token": self._token,
                }
                status = 200
            case ("custom_grant", self._client_id, self._client_secret, self._scope):
                # unsupported grant type
                result["error"] = "unsupported_grant_type"
                status = 400
            case (self._grant_type, self._client_id, self._client_secret, "wrong_scope"):
                # wrong scope
                result["error"] = "invalid_scope"
                status = 400
            case (self._grant_type, "wrong_client_id", self._client_secret, self._scope):
                # wrong client id
                result["error"] = "unauthorized_client"
                status = 400
            case (self._grant_type, self._client_id, "wrong_client_secret", self._scope):
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
