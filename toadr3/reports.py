import aiohttp

from .access_token import AccessToken
from .exceptions import ToadrError
from .models import Report


async def post_report(
    session: aiohttp.ClientSession,
    vtn_url: str,
    access_token: AccessToken | None,
    report: Report,
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

    Returns
    -------
    Report
        The report object returned by the VTN.

    Raises
    ------
    toadr3.ToadrError
        If the request to the VTN fails.
    """
    if report is None:
        raise ValueError("report is required")

    headers = {}
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
    extra_params: dict[str, str | int] | None = None,
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
    extra_params : dict[str, str | int] | None
        Extra query parameters to include in the request.

    Returns
    -------
    list[Report]
        A list of report objects.

    Raises
    ------
    ValueError
        If the query parameters are invalid.
    toadr3.ToadrException
        If the request to the VTN fails.
    """
    _check_arguments(skip, limit)
    params = _create_query_parameters(program_id, event_id, client_name, skip, limit)

    if extra_params is not None:
        # we don't want extra_params to overwrite the existing params
        params = extra_params | params

    headers = {}
    if access_token is not None:
        headers["Authorization"] = f"Bearer {access_token.token}"

    vtn_url = vtn_url.rstrip("/")

    async with session.get(f"{vtn_url}/reports", params=params, headers=headers) as response:
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
        for report in data:
            result.append(Report.model_validate(report))
        return result


def _create_query_parameters(
    program_id: str | None,
    event_id: str | None,
    client_name: str | None,
    skip: int | None,
    limit: int | None,
) -> dict[str, str | int]:
    """Create the query parameters for the get_reports function.

    Parameters
    ----------
    program_id : str | None
        The program ID to filter the events by.
    event_id : str | None
        The event ID to filter the events by.
    client_name : str | None
        The client name to filter the events by.
    skip : int | None
        The number of events to skip (for pagination).
    limit : int | None
        The maximum number of events to return.
    """
    params: dict[str, str | int] = {}
    if program_id is not None:
        params["programID"] = program_id
    if event_id is not None:
        params["eventID"] = event_id
    if client_name is not None:
        params["clientName"] = client_name
    if skip is not None:
        params["skip"] = skip
    if limit is not None:
        params["limit"] = limit
    return params


def _check_arguments(skip: int | None, limit: int | None) -> None:
    """
    Check the arguments for the get_events function.

    Parameters
    ----------
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
