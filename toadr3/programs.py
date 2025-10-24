import aiohttp

from toadr3 import AccessToken, ToadrError
from toadr3.models import Program, TargetType

from ._internal import ParameterBuilder, SkipAndLimit, Targets

_GET_PARAMS_BUILDER = ParameterBuilder(Targets, SkipAndLimit)


async def get_programs(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    target_type: TargetType | str | None = None,
    target_values: list[str] | None = None,
    skip: int | None = None,
    limit: int | None = None,
    extra_params: dict[str, str | int | list[str]] | None = None,
    custom_headers: dict[str, str] | None = None,
) -> list[Program]:
    """Get a list of programs from the VTN.

    List all programs known to the server.
    Use skip and pagination query params to limit response size.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    target_type: TargetType | str | None
        The target type to filter the programs by.
    target_values: list[str] | None
        The target values to filter the programs by (names of the target type).
    skip: int | None
        The number of programs to skip (for pagination).
    limit: int | None
        The maximum number of programs to return.
    extra_params: dict[str, str | int | list[str]] | None
        Extra query parameters to include in the request.
    custom_headers: dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    list[Program]
        A list of programs.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrError
        If the request to the VTN fails. Specifically, if the response status is 400, 403, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.
    """
    args = {
        "target_type": target_type,
        "target_values": target_values,
        "skip": skip,
        "limit": limit,
    }
    _GET_PARAMS_BUILDER.check_query_parameters(args)
    params = _GET_PARAMS_BUILDER.build_query_parameters(args, extra_params)

    headers: dict[str, str] = {}
    if custom_headers is not None:
        headers |= custom_headers

    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token.token}"

    vtn_url = vtn_url.rstrip("/")

    async with session.get(f"{vtn_url}/programs", params=params, headers=headers) as response:
        if not response.ok:
            match response.status:
                case 400 | 403 | 500:
                    json_response = await response.json()  # JSON should be of type Problem schema
                    message = json_response["title"]

                    if "detail" in json_response:
                        message = f"{message} - {json_response['detail']}"

                    raise ToadrError(
                        message,
                        status_code=response.status,
                        reason=response.reason,
                        headers=response.headers,  # type: ignore[arg-type]
                        json_response=json_response,
                    )
                case _:
                    raise RuntimeError(
                        f"Unexpected response status: {response.status} {response.reason}"
                    )

        data = await response.json()

        result = []
        for program in data:
            result.append(Program.model_validate(program))
        return result
