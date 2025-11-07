import aiohttp

from toadr3 import AccessToken
from toadr3.models import Program, TargetType

from ._internal import (
    ParameterBuilder,
    ProgramIDPathParameter,
    SkipAndLimit,
    Targets,
    delete_query,
    get_query,
    put_query,
)

_GET_PARAMS_BUILDER = ParameterBuilder(Targets, SkipAndLimit)
_GET_BY_ID_PARAMS_BUILDER = ParameterBuilder(ProgramIDPathParameter)


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

    data = await get_query(session, f"{vtn_url}/programs", access_token, params, custom_headers)

    if not isinstance(data, list):
        raise ValueError(f"Expected result to be a list. Got {type(data)} instead.")

    result = []
    for program in data:
        result.append(Program.model_validate(program))
    return result


async def get_program_by_id(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    program_id: str,
    custom_headers: dict[str, str] | None = None,
) -> Program:
    """Get a program by ID.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    program_id : str
        The program ID to search for.
    custom_headers : dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    Program
        The program object retrieved from the VTN.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, response status 400, 403, 404, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.
    """
    _GET_BY_ID_PARAMS_BUILDER.check_query_parameters({"program_id": program_id})

    data = await get_query(
        session,
        f"{vtn_url}/programs/{program_id}",
        access_token,
        custom_headers=custom_headers,
        accept_404=True,
    )

    return Program.model_validate(data)


async def delete_program_by_id(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    program_id: str,
    custom_headers: dict[str, str] | None = None,
) -> Program:
    """Delete a subscription by ID.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    program_id : str
        The program ID to search for.
    custom_headers : dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    Program
        The program object deleted from the VTN.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, response status 400, 403, 404, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.
    """
    _GET_BY_ID_PARAMS_BUILDER.check_query_parameters({"program_id": program_id})

    data = await delete_query(
        session,
        f"{vtn_url}/programs/{program_id}",
        access_token,
        custom_headers=custom_headers,
        accept_404=True,
    )

    return Program.model_validate(data)


async def put_program_by_id(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    program_id: str,
    program: Program,
    custom_headers: dict[str, str] | None = None,
) -> Program:
    """Update a program by ID.

    Parameters
    ----------
    session: aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url: str
        The URL of the VTN.
    access_token: AccessToken | None
        The access token to use for the request, use None if no token is required.
    program_id : str
        The program ID to search for.
    program: Program
        The program object with updated values.
    custom_headers : dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    Program
        The program object updated from the VTN.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails. Specifically, response status 400, 403, 404, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.
    """
    _GET_BY_ID_PARAMS_BUILDER.check_query_parameters({"program_id": program_id})

    if program is None:
        raise ValueError("program is required")

    data = program.model_dump_json(exclude_none=True, exclude_unset=True)

    if custom_headers is None:
        custom_headers = {}
    custom_headers["Content-Type"] = "application/json"

    data = await put_query(
        session,
        f"{vtn_url}/programs/{program_id}",
        access_token,
        body=data,
        custom_headers=custom_headers,
        accept_404=True,
    )

    return Program.model_validate(data)
