import aiohttp

from toadr3 import AccessToken
from toadr3.models import ObjectType, Subscription, TargetType

from ._internal import (
    ClientName,
    Objects,
    ParameterBuilder,
    ProgramID,
    SkipAndLimit,
    Targets,
    default_error_handler,
    get_query,
)

_GET_PARAMS_BUILDER = ParameterBuilder(ProgramID, ClientName, Targets, Objects, SkipAndLimit)


async def get_subscriptions(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    program_id: str | None = None,
    client_name: str | None = None,
    target_type: TargetType | str | None = None,
    target_values: list[str] | None = None,
    objects: list[str] | list[ObjectType] | None = None,
    skip: int | None = None,
    limit: int | None = None,
    extra_params: dict[str, str | int | list[str]] | None = None,
    custom_headers: dict[str, str] | None = None,
) -> list[Subscription]:
    """List all subscriptions.

    May filter results by programID and clientID as query params.
    May filter results by objects as query param. See objectTypes schema.
    Use skip and pagination query params to limit response size.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    program_id : str | None
        The program ID to filter the subscriptions by.
    client_name : str | None
        The client name to filter the subscriptions by.
    target_type: TargetType | str | None
        The target type to filter the subscriptions by.
    target_values: list[str] | None
        The target values to filter the subscriptions by (names of the target type).
    objects: list[str] | list[ObjectType] | None
        The object types to filter the subscriptions by.
    skip: int | None
        The number of subscriptions to skip (for pagination).
    limit: int | None
        The maximum number of subscriptions to return.
    extra_params: dict[str, str | int | list[str]] | None
        Extra query parameters to include in the request.
    custom_headers: dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    list[Subscription]
        A list of subscriptions.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, if the response status is 400, 403, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.

    """
    args = {
        "client_name": client_name,
        "program_id": program_id,
        "target_type": target_type,
        "target_values": target_values,
        "objects": objects,
        "skip": skip,
        "limit": limit,
    }
    _GET_PARAMS_BUILDER.check_query_parameters(args)
    params = _GET_PARAMS_BUILDER.build_query_parameters(args, extra_params)

    data = await get_query(
        session, f"{vtn_url}/subscriptions", access_token, params, custom_headers
    )

    if not isinstance(data, list):
        raise ValueError(f"Expected result to be a list. Got {type(data)} instead.")

    result = []
    for subscription in data:
        result.append(Subscription.model_validate(subscription))
    return result


async def post_subscription(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    subscription: Subscription,
    custom_headers: dict[str, str] | None = None,
) -> Subscription:
    """Create a new subscription.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    subscription: Subscription
        The subscription to create.
    custom_headers: dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    Subscription
        The subscription object created by the VTN.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, if the response status is 400, 403, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.

    """
    if subscription is None:
        raise ValueError("subscription is required")

    headers: dict[str, str] = {}
    if custom_headers is not None:
        headers |= custom_headers

    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token.token}"

    vtn_url = vtn_url.rstrip("/")

    data = subscription.model_dump_json(exclude_none=True, exclude_unset=True)
    headers["Content-Type"] = "application/json"

    async with session.post(f"{vtn_url}/subscriptions", headers=headers, data=data) as response:
        if not response.ok:
            match response.status:
                case 400 | 403 | 409 | 500:
                    await default_error_handler(response)
                case _:
                    await default_error_handler(response, "Unexpected error status!")

        data = await response.json()
        return Subscription.model_validate(data)
