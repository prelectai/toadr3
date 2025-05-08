import aiohttp

from .access_token import AccessToken
from .exceptions import ToadrError
from .models import Event, TargetType


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

    Returns
    -------
    list[Event]
        A list of events.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrError
        If the request to the VTN fails.
    """
    _check_arguments(target_type, target_values, skip, limit)

    params = _create_query_parameters(program_id, target_type, target_values, skip, limit)

    if extra_params is not None:
        # we don't want extra_params to overwrite the existing params
        params = extra_params | params

    headers = {}
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


def _create_query_parameters(
    program_id: str | None,
    target_type: TargetType | str | None,
    target_values: list[str] | None,
    skip: int | None,
    limit: int | None,
) -> dict[str, int | str | list[str]]:
    """Create the query parameters for the get_events function.

    Parameters
    ----------
    program_id : int | None
        The program ID to filter the events by.
    target_type : TargetType | str | None
        The target type to filter the events by.
    target_values : list[str] | None
        The target values to filter the events by (names of the target type).
    skip : int | None
        The number of events to skip (for pagination).
    limit : int | None
        The maximum number of events to return.
    """
    params: dict[str, int | str | list[str]] = {}
    if program_id is not None:
        params["programID"] = program_id

    if target_type is not None and target_values is not None:
        if isinstance(target_type, TargetType):
            params["targetType"] = target_type.value
        else:
            params["targetType"] = target_type  # should be string

        params["targetValues"] = target_values

    if skip is not None:
        params["skip"] = skip

    if limit is not None:
        params["limit"] = limit

    return params


def _check_arguments(
    target_type: TargetType | str | None,
    target_values: list[str] | None,
    skip: int | None,
    limit: int | None,
) -> None:
    """
    Check the arguments for the get_events function.

    Parameters
    ----------
    target_type : TargetType | str | None
        The target type to filter the events by.
    target_values : list[str] | None
        The target values to filter the events by (names of the target type).
    skip : int | None
        The number of events to skip (for pagination).
    limit : int | None
        The maximum number of events to return.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    """
    errors = []
    if target_type is not None and target_values is None:
        errors.append("target_values are required when target_type is provided")

    if target_values is not None and target_type is None:
        errors.append("target_type is required when target_values are provided")

    if target_values is not None and not isinstance(target_values, list):
        errors.append("target_values must be a list of strings")

    if target_type is not None and not isinstance(target_type, (TargetType, str)):
        errors.append("target_type must be TargetType or str")

    if skip is not None and not isinstance(skip, int):
        errors.append("skip must be an integer")

    if skip is not None and isinstance(skip, int) and skip < 0:
        errors.append("skip must be a positive integer")

    if limit is not None and not isinstance(limit, int):
        errors.append("limit must be an integer")

    if limit is not None and isinstance(limit, int) and limit < 0:
        errors.append("limit must be a positive integer")

    if errors:
        raise ValueError(", ".join(errors))
