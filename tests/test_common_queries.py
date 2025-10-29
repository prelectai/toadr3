import pytest
from _common_test_utils import QueryFunction, check_functions_raises

from toadr3 import (
    ToadrClient,
    ToadrError,
    get_events,
    get_programs,
    get_reports,
    get_subscriptions,
    models,
)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_subscriptions,
    ],
)
async def test_target_type_is_none(function: QueryFunction, client: ToadrClient) -> None:
    msg = "target_type is required when target_values are provided"
    kwargs = {
        "target_type": None,
        "target_values": ["121"],
    }
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_subscriptions,
    ],
)
async def test_target_type_is_not_str_or_target_type(
    function: QueryFunction, client: ToadrClient
) -> None:
    msg = "target_type must be TargetType or str"
    kwargs = {
        "target_type": 1,
        "target_values": ["121"],
    }
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_subscriptions,
    ],
)
async def test_target_values_is_none(function: QueryFunction, client: ToadrClient) -> None:
    msg = "target_values are required when target_type is provided"
    kwargs = {
        "target_type": models.TargetType.SERVICE_AREA,
        "target_values": None,
    }
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_subscriptions,
    ],
)
async def test_target_values_not_list(function: QueryFunction, client: ToadrClient) -> None:
    msg = "target_values must be a list of strings"
    kwargs = {
        "target_type": models.TargetType.SERVICE_AREA,
        "target_values": "121",
    }
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_skip_not_int(function: QueryFunction, client: ToadrClient) -> None:
    msg = "skip must be an integer"
    kwargs = {"skip": "0"}
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_skip_negative(function: QueryFunction, client: ToadrClient) -> None:
    msg = "skip must be a positive integer"
    kwargs = {"skip": -1}
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_limit_not_int(function: QueryFunction, client: ToadrClient) -> None:
    msg = "limit must be an integer"
    kwargs = {"limit": "0"}
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_limit_out_of_range_negative(function: QueryFunction, client: ToadrClient) -> None:
    msg = "limit must be a positive integer"
    kwargs = {"limit": -1}
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_multiple_errors(function: QueryFunction, client: ToadrClient) -> None:
    msg = "skip must be a positive integer, limit must be a positive integer"
    kwargs = {"skip": -1, "limit": -1}
    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_forbidden(function: QueryFunction, client: ToadrClient) -> None:
    token = await client.token
    assert token is not None
    token._token = "invalid"  # noqa: SLF001

    msg = "Forbidden 403 - Invalid or missing access token"
    await check_functions_raises(function, {}, msg, client, ToadrError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_with_custom_header(function: QueryFunction, client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    kwargs = {"custom_headers": {"X-Custom-Header": "CustomValue"}}
    all_items = await function(session, vtn_url, token)

    items = await function(session, vtn_url, token, **kwargs)
    assert len(items) == len(all_items)

    items = await getattr(client, function.__name__)(**kwargs)
    assert len(items) == len(all_items)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_with_custom_header_invalid_value(
    function: QueryFunction, client: ToadrClient
) -> None:
    msg = "Invalid value for X-Custom-Header: InvalidValue"
    kwargs = {"custom_headers": {"X-Custom-Header": "InvalidValue"}}
    await check_functions_raises(function, kwargs, msg, client, ToadrError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_with_extra_query_parameters(function: QueryFunction, client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    pydantic_items = await function(session, vtn_url, token)
    all_items = [dict(item) for item in pydantic_items]

    expected_odd_ids = {item["id"] for item in all_items if int(item["id"]) % 2 == 1}
    expected_even_ids = {item["id"] for item in all_items if int(item["id"]) % 2 == 0}

    # Check even
    result = await function(session, vtn_url, token, extra_params={"x-parity": "even"})
    result_ids = {dict(item)["id"] for item in result}
    assert result_ids == expected_even_ids

    result = await getattr(client, function.__name__)(extra_params={"x-parity": "even"})
    result_ids = {dict(item)["id"] for item in result}
    assert result_ids == expected_even_ids

    # Check odd
    result = await function(session, vtn_url, token, extra_params={"x-parity": "odd"})
    result_ids = {dict(item)["id"] for item in result}
    assert result_ids == expected_odd_ids

    result = await getattr(client, function.__name__)(extra_params={"x-parity": "odd"})
    result_ids = {dict(item)["id"] for item in result}
    assert result_ids == expected_odd_ids

    # Check invalid
    kwargs = {"extra_params": {"x-parity": "invalid"}}
    msg = "Bad Request 400 - Invalid value for x-parity: invalid"
    await check_functions_raises(function, kwargs, msg, client, ToadrError)


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_with_skip(function: QueryFunction, client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    all_items = await function(session, vtn_url, token)

    kwargs = {"skip": 1}

    items = await function(session, vtn_url, token, **kwargs)
    assert items == all_items[1:]

    items = await getattr(client, function.__name__)(**kwargs)
    assert items == all_items[1:]


@pytest.mark.parametrize(
    "function",
    [
        get_events,
        get_programs,
        get_reports,
        get_subscriptions,
    ],
)
async def test_with_limit(function: QueryFunction, client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    all_items = await function(session, vtn_url, token)

    kwargs = {"limit": 2}

    items = await function(session, vtn_url, token, **kwargs)
    assert items == all_items[:2]

    items = await getattr(client, function.__name__)(**kwargs)
    assert items == all_items[:2]


@pytest.mark.parametrize(
    ("function", "pid"),
    [
        (get_events, "34"),
        (get_reports, "1"),
        (get_subscriptions, "6"),
    ],
)
async def test_with_program_id(
    function: QueryFunction,
    client: ToadrClient,
    pid: str,
) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    all_items = await function(session, vtn_url, token)
    filtered_items = [item for item in all_items if getattr(item, "program_id", None) == pid]
    assert len(filtered_items) > 0, "No items found with program_id '1' for testing."

    kwargs = {"program_id": pid}

    items = await function(session, vtn_url, token, **kwargs)
    assert items == filtered_items

    items = await getattr(client, function.__name__)(**kwargs)
    assert items == filtered_items


@pytest.mark.parametrize(
    ("function", "pid"),
    [
        (get_events, "33"),
        (get_reports, "2"),
        (get_subscriptions, "7"),
    ],
)
async def test_with_program_id_no_match(
    function: QueryFunction,
    client: ToadrClient,
    pid: str,
) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    kwargs = {"program_id": pid}

    events = await function(session, vtn_url, token, **kwargs)
    assert len(events) == 0

    events = await getattr(client, function.__name__)(**kwargs)
    assert len(events) == 0


@pytest.mark.parametrize(
    "function",
    [
        get_reports,
        get_subscriptions,
    ],
)
async def test_with_client_name(
    function: QueryFunction,
    client: ToadrClient,
) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    all_items = await function(session, vtn_url, token)
    filtered_items = [item for item in all_items if getattr(item, "client_name", None) == "YAC"]
    assert len(filtered_items) > 0, "No items found with program_id '1' for testing."

    kwargs = {"client_name": "YAC"}

    items = await function(session, vtn_url, token, **kwargs)
    assert items == filtered_items

    items = await getattr(client, function.__name__)(**kwargs)
    assert items == filtered_items


@pytest.mark.parametrize(
    "function",
    [
        get_reports,
        get_subscriptions,
    ],
)
async def test_with_client_name_no_match(function: QueryFunction, client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    kwargs = {"client_name": "non-existent-client"}

    events = await function(session, vtn_url, token, **kwargs)
    assert len(events) == 0

    events = await getattr(client, function.__name__)(**kwargs)
    assert len(events) == 0


@pytest.mark.parametrize(
    "function",
    [
        get_subscriptions,
    ],
)
async def test_with_objects_not_a_list(function: QueryFunction, client: ToadrClient) -> None:
    msg = "objects must be a list of strings or ObjectType"
    kwargs = {"objects": "not a list"}

    await check_functions_raises(function, kwargs, msg, client, ValueError)


@pytest.mark.parametrize(
    "function",
    [
        get_subscriptions,
    ],
)
async def test_with_objects_not_object_type_or_string(
    function: QueryFunction, client: ToadrClient
) -> None:
    match_msg = (
        "object type '1' must be of type string or ObjectType, "
        "object type '2' must be of type string or ObjectType"
    )
    kwargs = {"objects": [1, 2]}
    await check_functions_raises(function, kwargs, match_msg, client, ValueError)
