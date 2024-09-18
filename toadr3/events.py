from enum import Enum

import aiohttp

from .access_token import AccessToken
from .event import Event
from .exceptions import ToadrError


class TargetType(Enum):
    """Enumeration of target types."""

    POWER_SERVICE_LOCATION = "POWER_SERVICE_LOCATION"
    """
    A Power Service Location is a utility named specific location in geography or
    the distribution system, usually the point of service to a customer site.
    """
    SERVICE_AREA = "SERVICE_AREA"
    """
    A Service Area is a utility named geographic region.
    Target values array contains a string representing a service area name.
    """
    GROUP = "GROUP"
    """
    Target values array contains a string representing a group.
    """
    RESOURCE_NAME = "RESOURCE_NAME"
    """
    Target values array contains a string representing a resource name.
    """
    VEN_NAME = "VEN_NAME"
    """
    Target values array contains a string representing a VEN name.
    """
    EVENT_NAME = "EVENT_NAME"
    """
    Target values array contains a string representing an event name.
    """
    PROGRAM_NAME = "PROGRAM_NAME"
    """
    Target values array contains a string representing a program name.
    """


async def get_events(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    program_id: str | None = None,
    target_type: TargetType | None = None,
    target_values: list[str] | None = None,
    skip: int | None = None,
    limit: int | None = None,
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
    program_id : int | None
        The program ID to filter the events by.
    target_type : TargetType | None
        The target type to filter the events by.
    target_values : list[str] | None
        The target values to filter the events by (names of the target type).
    skip : int | None
        The number of events to skip (for pagination).
    limit : int | None
        The maximum number of events to return.

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

    headers = {}
    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token.token}"

    while vtn_url.endswith("/"):
        vtn_url = vtn_url[:-1]

    async with session.get(f"{vtn_url}/events", params=params, headers=headers) as response:
        # 400 is start of HTTP error codes
        if response.status >= 400:  # noqa PLR2004 - Magic value used in comparison
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
                        headers=response.headers,
                        json_response=json_response,
                    )
                case _:
                    raise RuntimeError(
                        f"Unexpected response status: {response.status} {response.reason}"
                    )

        data = await response.json()

        result = []
        for event in data:
            result.append(Event(event))
        return result


def _create_query_parameters(
    program_id: int | None,
    target_type: TargetType | None,
    target_values: list[str] | None,
    skip: int | None,
    limit: int | None,
) -> dict[str, int | str | list[str]]:
    """Create the query parameters for the get_events function.

    Parameters
    ----------
    program_id : int | None
        The program ID to filter the events by.
    target_type : TargetType | None
        The target type to filter the events by.
    target_values : list[str] | None
        The target values to filter the events by (names of the target type).
    skip : int | None
        The number of events to skip (for pagination).
    limit : int | None
        The maximum number of events to return.
    """
    params = {}
    if program_id is not None:
        params["programID"] = program_id

    if target_type is not None:
        params["targetType"] = target_type.value
        params["targetValues"] = target_values

    if skip is not None:
        params["skip"] = skip

    if limit is not None:
        params["limit"] = limit

    return params


def _check_arguments(
    target_type: TargetType | None,
    target_values: list[str] | None,
    skip: int | None,
    limit: int | None,
):
    """
    Check the arguments for the get_events function.

    Parameters
    ----------
    target_type : TargetType | None
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
    if target_type is not None and target_values is None:
        raise ValueError("target_values are required when target_type is provided")

    if target_values is not None and target_type is None:
        raise ValueError("target_type is required when target_values are provided")

    if target_values is not None and not isinstance(target_values, list):
        raise ValueError("target_values must be a list of strings")

    if skip is not None and not isinstance(skip, int):
        raise ValueError("skip must be an integer")

    if skip is not None and skip < 0:
        raise ValueError("skip must be a positive integer")

    if limit is not None and not isinstance(limit, int):
        raise ValueError("limit must be an integer")

    if limit is not None and not limit >= 0:
        raise ValueError("limit must be a positive integer")
