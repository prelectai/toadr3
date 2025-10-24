from typing import Protocol

import aiohttp
import pytest
from aiohttp import ClientSession

from toadr3 import AccessToken, ToadrError, get_events, get_programs, get_reports, models
from toadr3.models import DocstringBaseModel


class QueryFunction(Protocol):
    """A protocol for query functions like get_events and get_programs."""

    async def __call__(
        self,
        session: aiohttp.ClientSession | None,
        vtn_url: str | None,
        access_token: AccessToken | None,
        **kwargs: object,
    ) -> list[DocstringBaseModel]:
        """Signature with common parameters for query functions."""


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
    ],
)
async def test_target_type_is_none(function: QueryFunction) -> None:
    msg = "target_type is required when target_values are provided"
    with pytest.raises(ValueError, match=msg):
        _ = await function(None, "", None, target_values=["121"])


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
    ],
)
async def test_target_type_is_not_str_or_target_type(function: QueryFunction) -> None:
    msg = "target_type must be TargetType or str"
    with pytest.raises(ValueError, match=msg):
        _ = await function(None, "", None, target_type=1, target_values=["121"])


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
    ],
)
async def test_target_values_is_none(function: QueryFunction) -> None:
    msg = "target_values are required when target_type is provided"
    with pytest.raises(ValueError, match=msg):
        _ = await function(None, "", None, target_type=models.TargetType.SERVICE_AREA)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
    ],
)
async def test_target_values_not_list(function: QueryFunction) -> None:
    msg = "target_values must be a list of strings"
    with pytest.raises(ValueError, match=msg):
        _ = await function(
            None,
            "",
            None,
            target_type=models.TargetType.SERVICE_AREA,
            target_values="121",
        )


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_skip_not_int(function: QueryFunction) -> None:
    msg = "skip must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await function(None, "", None, skip="0")


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_skip_negative(function: QueryFunction) -> None:
    msg = "skip must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await function(None, "", None, skip=-1)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_limit_not_int(function: QueryFunction) -> None:
    msg = "limit must be an integer"
    with pytest.raises(ValueError, match=msg):
        _ = await function(None, "", None, limit="0")


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_limit_out_of_range_negative(function: QueryFunction) -> None:
    msg = "limit must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await function(None, "", None, limit=-1)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_multiple_errors(function: QueryFunction) -> None:
    msg = "skip must be a positive integer, limit must be a positive integer"
    with pytest.raises(ValueError, match=msg):
        _ = await function(None, "", None, skip=-1, limit=-1)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_forbidden(session: ClientSession, function: QueryFunction) -> None:
    with pytest.raises(ToadrError, match="Forbidden"):
        _ = await function(session, "", None)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_with_custom_header(
    session: ClientSession, token: AccessToken, function: QueryFunction
) -> None:
    all_items = await function(session, "", token)
    items = await function(session, "", token, custom_headers={"X-Custom-Header": "CustomValue"})

    assert len(items) == len(all_items)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_with_custom_header_invalid_value(
    session: ClientSession, token: AccessToken, function: QueryFunction
) -> None:
    with pytest.raises(ToadrError, match="Invalid value for X-Custom-Header: InvalidValue"):
        _ = await function(
            session,
            "",
            token,
            custom_headers={"X-Custom-Header": "InvalidValue"},
        )


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_with_extra_query_parameters(
    session: ClientSession, token: AccessToken, function: QueryFunction
) -> None:
    pydantic_items = await function(session, "", token)
    all_items = [dict(item) for item in pydantic_items]

    expected_odd_ids = {item["id"] for item in all_items if int(item["id"]) % 2 == 1}
    expected_even_ids = {item["id"] for item in all_items if int(item["id"]) % 2 == 0}

    result = await function(session, "", token, extra_params={"x-parity": "even"})
    even_ids = {dict(item)["id"] for item in result}

    assert even_ids == expected_even_ids

    result = await function(session, "", token, extra_params={"x-parity": "odd"})
    odd_ids = {dict(item)["id"] for item in result}
    assert odd_ids == expected_odd_ids

    with pytest.raises(ToadrError):
        _ = await function(session, "", token, extra_params={"x-parity": "invalid"})


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_with_skip(
    session: ClientSession, token: AccessToken, function: QueryFunction
) -> None:
    all_items = await function(session, "", token)
    items = await function(session, "", token, skip=1)
    assert items == all_items[1:]


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
    ],
)
async def test_with_limit(
    session: ClientSession, token: AccessToken, function: QueryFunction
) -> None:
    all_items = await function(session, "", token)
    items = await function(session, "", token, limit=2)
    assert items == all_items[:2]


@pytest.mark.parametrize(
    ("function", "pid"),
    [
        (get_events, "34"),
        (get_reports, "1"),
    ],
)
async def test_with_program_id(
    session: ClientSession, token: AccessToken, function: QueryFunction, pid: str
) -> None:
    all_items = await function(session, "", token)
    filtered_items = [item for item in all_items if getattr(item, "program_id", None) == pid]
    assert len(filtered_items) > 0, "No items found with program_id '1' for testing."

    items = await function(session, "", token, program_id=pid)
    assert items == filtered_items


@pytest.mark.parametrize(
    ("function", "pid"),
    [
        (get_events, "33"),
        (get_reports, "2"),
    ],
)
async def test_with_program_id_no_match(
    session: ClientSession, token: AccessToken, function: QueryFunction, pid: str
) -> None:
    events = await function(session, "", token, program_id=pid)
    assert len(events) == 0


@pytest.mark.parametrize(
    "function",
    [
        get_reports,
    ],
)
async def test_with_client_name(
    session: ClientSession,
    token: AccessToken,
    function: QueryFunction,
) -> None:
    all_items = await function(session, "", token)
    filtered_items = [item for item in all_items if getattr(item, "client_name", None) == "YAC"]
    assert len(filtered_items) > 0, "No items found with program_id '1' for testing."

    items = await function(session, "", token, client_name="YAC")
    assert items == filtered_items


@pytest.mark.parametrize(
    "function",
    [
        get_reports,
    ],
)
async def test_with_client_name_no_match(
    session: ClientSession, token: AccessToken, function: QueryFunction
) -> None:
    events = await function(session, "", token, client_name="non-existent-client")
    assert len(events) == 0
