import aiohttp

from ._internal import ParameterBuilder, ProgramID, SkipAndLimit, Targets, get_query
from .access_token import AccessToken
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

    data = await get_query(session, f"{vtn_url}/events", access_token, params, custom_headers)

    if not isinstance(data, list):
        raise ValueError(f"Expected result to be a list. Got {type(data)} instead.")

    result = []
    for event in data:
        result.append(Event.model_validate(event))
    return result
