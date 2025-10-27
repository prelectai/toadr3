import aiohttp

from ._internal import ClientName, EventID, ParameterBuilder, ProgramID, SkipAndLimit, get_query
from .access_token import AccessToken
from .exceptions import ToadrError
from .models import Report

_GET_PARAMS_BUILDER = ParameterBuilder(ProgramID, EventID, ClientName, SkipAndLimit)


async def post_report(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    report: Report,
    custom_headers: dict[str, str] | None = None,
) -> Report:
    """Post a report to the VTN.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url : str
        The URL of the VTN.
    access_token : AccessToken | None
        The access token to use for the request, use None if no token is required.
    report : Report
        The report object to post.
    custom_headers : dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    Report
        The report object returned by the VTN.

    Raises
    ------
    toadr3.ToadrError
        If the request to the VTN fails. Specifically, if the
        response status is 400, 403, 409, or 500,
    aiohttp.ClientError
        If there is an unexpected error with the HTTP request to the VTN.
    """
    if report is None:
        raise ValueError("report is required")

    headers: dict[str, str] = {}
    if custom_headers is not None:
        headers |= custom_headers

    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token.token}"

    vtn_url = vtn_url.rstrip("/")

    data = report.model_dump_json(exclude_none=True, exclude_unset=True)
    headers["Content-Type"] = "application/json"

    async with session.post(f"{vtn_url}/reports", headers=headers, data=data) as response:
        if not response.ok:
            match response.status:
                case 400 | 403 | 409 | 500:
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
        return Report.model_validate(data)


async def get_reports(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    program_id: str | None = None,
    event_id: str | None = None,
    client_name: str | None = None,
    skip: int | None = None,
    limit: int | None = None,
    extra_params: dict[str, str | int | list[str]] | None = None,
    custom_headers: dict[str, str] | None = None,
) -> list[Report]:
    """Get a list of reports from the VTN.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp session to use for the request.
    vtn_url : str
        The URL of the VTN.
    access_token : AccessToken | None
        The access token to use for the request, use None if no token is required.
    program_id : str | None
        The program ID to filter the reports by.
    event_id : str | None
        The event ID to filter the reports by.
    client_name : str | None
        The client name to filter the reports by.
    skip : int | None
        The number of reports to skip (for pagination).
    limit : int | None
        The maximum number of reports to return.
    extra_params : dict[str, str | int | list[str]] | None
        Extra query parameters to include in the request.
    custom_headers : dict[str, str] | None
        Extra headers to include in the request.

    Returns
    -------
    list[Report]
        A list of report objects.

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
        "event_id": event_id,
        "program_id": program_id,
        "skip": skip,
        "limit": limit,
    }
    _GET_PARAMS_BUILDER.check_query_parameters(args)
    params = _GET_PARAMS_BUILDER.build_query_parameters(args, extra_params)
    data = await get_query(session, f"{vtn_url}/reports", access_token, params, custom_headers)

    if not isinstance(data, list):
        raise ValueError(f"Expected result to be a list. Got {type(data)} instead.")

    result = []
    for report in data:
        result.append(Report.model_validate(report))
    return result
