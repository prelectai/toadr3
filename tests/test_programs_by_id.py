from collections.abc import Awaitable, Callable
from typing import Protocol

import pytest
from testdata import default_program_model

from toadr3 import (
    ToadrClient,
    ToadrError,
    delete_program_by_id,
    get_program_by_id,
    put_program_by_id,
)
from toadr3.models import Subscription

FUNCTIONS = {
    "delete_program": delete_program_by_id.__name__,
    "get_program": get_program_by_id.__name__,
    "put_program": put_program_by_id.__name__,
}


class ItemsWithID(Protocol):
    """Protocol for objects with an ID attribute."""

    id: str


def get_query_function(func_name: str) -> Callable[..., Awaitable[ItemsWithID | None]]:
    """Get the query function based on the function name."""
    query_function_name = FUNCTIONS[func_name]
    return globals()[query_function_name]  # type: ignore[no-any-return]


@pytest.mark.parametrize(
    ("func_name", "args"),
    [
        ("delete_program", ("2",)),
        ("get_program", ("2",)),
        ("put_program", ("2", default_program_model())),
    ],
)
async def test_by_id(client: ToadrClient, func_name: str, args: tuple[str, Subscription]) -> None:
    result = await getattr(client, func_name)(*args)
    assert result is not None
    assert result.id == args[0]

    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    query_function = get_query_function(func_name)
    result = await query_function(session, vtn_url, token, *args)
    assert result is not None
    assert result.id == args[0]


@pytest.mark.parametrize(
    ("func_name", "args"),
    [
        ("delete_program", ("3",)),
        ("get_program", ("3",)),
        ("put_program", ("3", default_program_model())),
    ],
)
async def test_by_id_not_found(
    client: ToadrClient, func_name: str, args: tuple[str, Subscription]
) -> None:
    result = await getattr(client, func_name)(*args)
    assert result is None

    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    msg = f"Not Found 404 - Unable to find program with id: '{args[0]}'"
    query_function = get_query_function(func_name)
    with pytest.raises(ToadrError, match=msg):
        _ = await query_function(session, vtn_url, token, *args)


@pytest.mark.parametrize(
    "item_id",
    [
        2,
        True,
    ],
)
@pytest.mark.parametrize(
    "func_name",
    [
        "delete_program",
        "get_program",
        "put_program",
    ],
)
async def test_by_id_invalid_id(client: ToadrClient, func_name: str, item_id: object) -> None:
    if func_name.startswith("put"):  # noqa: SIM108
        args = (item_id, default_program_model())
    else:
        args = (item_id,)  # type: ignore[assignment]

    msg = "program_id must be a string"
    with pytest.raises(ValueError, match=msg):
        _ = await getattr(client, func_name)(*args)

    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    query_function = get_query_function(func_name)
    with pytest.raises(ValueError, match=msg):
        _ = await query_function(session, vtn_url, token, *args)


@pytest.mark.parametrize(
    ("func_name", "args"),
    [
        ("delete_program", (None,)),
        ("get_program", (None,)),
        ("put_program", (None, default_program_model())),
    ],
)
async def test_by_id_none(
    client: ToadrClient, func_name: str, args: tuple[str, Subscription]
) -> None:
    arg = "program_id cannot be None"
    with pytest.raises(ValueError, match=arg):
        _ = await getattr(client, func_name)(*args)

    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    query_function = get_query_function(func_name)
    with pytest.raises(ValueError, match=arg):
        _ = await query_function(session, vtn_url, token, *args)


@pytest.mark.parametrize(
    ("func_name", "args"),
    [
        ("delete_program", ("2",)),
        ("get_program", ("2",)),
        ("put_program", ("2", default_program_model())),
    ],
)
async def test_by_id_custom_headers(
    client: ToadrClient, func_name: str, args: tuple[str, Subscription]
) -> None:
    custom_headers = {
        "X-Custom-Header": "CustomValue",
    }

    result = await getattr(client, func_name)(*args, custom_headers=custom_headers)
    assert result is not None
    assert result.id == args[0]

    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    query_function = get_query_function(func_name)
    result = await query_function(session, vtn_url, token, *args, custom_headers=custom_headers)
    assert result is not None
    assert result.id == args[0]


@pytest.mark.parametrize(
    ("func_name", "args"),
    [
        ("delete_program", ("2",)),
        ("get_program", ("2",)),
        ("put_program", ("2", default_program_model())),
    ],
)
async def test_by_id_custom_headers_failure(
    client: ToadrClient, func_name: str, args: tuple[str, Subscription]
) -> None:
    custom_headers = {
        "X-Custom-Header": "InvalidValue",
    }

    msg = "Bad Request 400 - Invalid value for X-Custom-Header: InvalidValue"

    with pytest.raises(ToadrError, match=msg):
        _ = await getattr(client, func_name)(*args, custom_headers=custom_headers)

    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    query_function = get_query_function(func_name)
    with pytest.raises(ToadrError, match=msg):
        _ = await query_function(session, vtn_url, token, *args, custom_headers=custom_headers)


async def test_by_id_put(client: ToadrClient) -> None:
    program = default_program_model()
    program.id = "2"
    program.program_name = "Updated Program Name"
    assert program.created_date_time is None
    assert program.modification_date_time is None

    orig = await client.get_program("2")
    assert orig is not None
    assert orig.created_date_time is not None
    assert orig.modification_date_time is not None

    result = await client.put_program("2", program)
    assert result is not None
    assert result.id == "2"
    assert result.program_name == "Updated Program Name"
    assert result.modification_date_time is not None
    assert result.modification_date_time > orig.modification_date_time
    assert result.created_date_time == orig.created_date_time
