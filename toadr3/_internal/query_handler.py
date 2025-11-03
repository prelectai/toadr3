from typing import Any

import aiohttp

from toadr3.access_token import AccessToken
from toadr3.exceptions import ToadrError


async def default_error_handler(response: aiohttp.ClientResponse, msg: str | None = None) -> None:
    """Error handler that generates a ToadrError from a Problem JSON response.

    Parameters
    ----------
    response: aiohttp.ClientResponse
        Response from server
    msg: str | None
        Pre-message to add to the message.

    Raises
    ------
    ToadrError
        Raises a ToadrError from a Problem JSON response.
    """
    json_response = await response.json()  # JSON should be of type Problem schema
    status = response.status

    message = ""
    if msg is not None:
        message = f"{msg} "

    if "title" in json_response:
        message += json_response["title"]
    else:
        message += f"Unexpected response type: {json_response}"

    if "detail" in json_response:
        message = f"{message} {status} - {json_response['detail']}"

    raise ToadrError(
        message,
        status_code=response.status,
        reason=response.reason,
        headers=response.headers,  # type: ignore[arg-type]
        json_response=json_response,
    )


async def _query(
    method: str,
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    body: str | None = None,
    params: dict[str, str | int | list[str]] | None = None,
    custom_headers: dict[str, str] | None = None,
    accept_404: bool = False,
) -> Any:  # noqa: ANN401
    """Perform query with some default behaviour.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    body: str | None
        The JSON body to include in the request.
    params: dict[str, str | int | list[str]] | None
        Extra query parameters to include in the request.
    custom_headers: dict[str, str] | None
        Extra headers to include in the request.
    accept_404: bool
        Flag to indicate if the API can return a 404 response.

    Returns
    -------
    Any
        The response parsed as JSON.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, if the response status is 400, 403, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.

    """
    headers: dict[str, str] = {}
    if custom_headers is not None:
        headers |= custom_headers

    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token.token}"

    vtn_url = vtn_url.rstrip("/")
    async with session.request(
        method, vtn_url, params=params, headers=headers, data=body
    ) as response:
        if not response.ok:
            match response.status:
                case 400 | 403 | 500:
                    await default_error_handler(response)
                case 404 if accept_404:
                    await default_error_handler(response)
                case _:
                    await default_error_handler(response, "Unexpected error status!")

        return await response.json()


async def get_query(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    params: dict[str, str | int | list[str]] | None = None,
    custom_headers: dict[str, str] | None = None,
    accept_404: bool = False,
) -> Any:  # noqa: ANN401
    """Perform default handling of a GET query.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    params: dict[str, str | int | list[str]] | None
        Extra query parameters to include in the request.
    custom_headers: dict[str, str] | None
        Extra headers to include in the request.
    accept_404: bool
        Flag to indicate if the API can return a 404 response.

    Returns
    -------
    Any
        The response parsed as JSON.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, if the response status is 400, 403, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.

    """
    return await _query(
        "GET", session, vtn_url, access_token, None, params, custom_headers, accept_404
    )


async def delete_query(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    params: dict[str, str | int | list[str]] | None = None,
    custom_headers: dict[str, str] | None = None,
    accept_404: bool = False,
) -> Any:  # noqa: ANN401
    """Perform default handling of a DELETE query.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    params: dict[str, str | int | list[str]] | None
        Extra query parameters to include in the request.
    custom_headers: dict[str, str] | None
        Extra headers to include in the request.
    accept_404: bool
        Flag to indicate if the API can return a 404 response.

    Returns
    -------
    Any
        The response parsed as JSON.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, if the response status is 400, 403, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.

    """
    return await _query(
        "DELETE", session, vtn_url, access_token, None, params, custom_headers, accept_404
    )


async def put_query(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    body: str,
    params: dict[str, str | int | list[str]] | None = None,
    custom_headers: dict[str, str] | None = None,
    accept_404: bool = False,
) -> Any:  # noqa: ANN401
    """Perform default handling of a PUT query.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    body: str
        The body to include in the PUT request.
    params: dict[str, str | int | list[str]] | None
        Extra query parameters to include in the request.
    custom_headers: dict[str, str] | None
        Extra headers to include in the request.
    accept_404: bool
        Flag to indicate if the API can return a 404 response.

    Returns
    -------
    Any
        The response parsed as JSON.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, if the response status is 400, 403, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.

    """
    return await _query(
        "PUT", session, vtn_url, access_token, body, params, custom_headers, accept_404
    )
