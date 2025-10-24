import aiohttp

from ._internal import ParameterBuilder, ProgramID, SkipAndLimit, Targets
from .access_token import AccessToken
from .exceptions import ToadrError
from .models import Event, TargetType

_GET_PARAMS_BUILDER = ParameterBuilder(ProgramID, Targets, SkipAndLimit)


async def get_events(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    program_id: str | None = None,
    target_type: TargetType | str | None = None,
    target_values: list[str] | None = None,
    skip: int | None = None,
    limit: int | None = None,
    extra_params: dict[str, str | int | list[str]] | None = None,
    custom_headers: dict[str, str] | None = None,
) -> list[Event]:
    """Get a list of events from the VTN.

    Lists all the events available from the VTN.
    The results can be filtered by providing a program ID, and/or target type and target values.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url : str
        The URL of the VTN.
    access_token : AccessToken | None
        The access token to use for the request, use None if no token is required.
    program_id : str | None
        The program ID to filter the events by.
    target_type : TargetType | str | None
        The target type to filter the events by.
    target_values : list[str] | None
        The target values to filter the events by (names of the target type).
    skip : int | None
        The number of events to skip (for pagination).
    limit : int | None
        The maximum number of events to return.
    extra_params : dict[str, str | int | list[str]] | None
        Extra query parameters to include in the request.
    custom_headers : dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    list[Event]
        A list of events.

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
        "program_id": program_id,
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

    async with session.get(f"{vtn_url}/events", params=params, headers=headers) as response:
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
        for event in data:
            result.append(Event.model_validate(event))
        return result
