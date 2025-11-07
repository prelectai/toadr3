import pytest
from pydantic import BaseModel
from testdata import default_program_model, default_report_model, default_subscription_model

import toadr3


async def test_client_context_manager(client: toadr3.ToadrClient) -> None:
    async with client:
        assert await client.token is not None
        assert client.client_session is not None
        assert client.vtn_url == "vtn_url"

    assert client.closed

    with pytest.raises(RuntimeError, match="Client is closed"):
        async with client:
            pass


@pytest.mark.parametrize(
    ("method_name", "method_args"),
    [
        ("get_programs", ()),
        ("delete_program", ("id",)),
        ("get_program", ("id",)),
        ("put_program", ("id", default_program_model())),
        ("get_events", ()),
        ("get_reports", ()),
        ("post_report", (default_report_model(),)),
        ("get_subscriptions", ()),
        ("delete_subscription", ("id",)),
        ("get_subscription", ("id",)),
        ("put_subscription", ("id", default_subscription_model())),
        ("post_subscription", (default_subscription_model(),)),
    ],
)
async def test_client_default_custom_headers_passthrough(
    client: toadr3.ToadrClient, method_name: str, method_args: tuple[BaseModel]
) -> None:
    # Test that default_custom_headers are set and forwarded correctly
    assert client.default_custom_headers == {}

    custom_headers = {"X-Custom-Header": "InvalidValue"}
    client_with_headers = toadr3.ToadrClient(
        vtn_url="vtn_url",
        oauth_config=client._oauth_config,  # noqa: SLF001
        session=client.client_session,
        default_custom_headers=custom_headers,
    )
    assert client_with_headers.default_custom_headers == custom_headers

    msg = "Bad Request 400 - Invalid value for X-Custom-Header: InvalidValue"
    with pytest.raises(toadr3.ToadrError, match=msg):
        _ = await getattr(client_with_headers, method_name)(*method_args)


@pytest.mark.parametrize(
    ("method_name", "method_args"),
    [
        ("get_programs", ()),
        ("delete_program", ("id",)),
        ("get_program", ("id",)),
        ("put_program", ("id", default_program_model())),
        ("get_events", ()),
        ("get_reports", ()),
        ("post_report", (default_report_model(),)),
        ("get_subscriptions", ()),
        ("delete_subscription", ("id",)),
        ("get_subscription", ("id",)),
        ("put_subscription", ("id", default_subscription_model())),
        ("post_subscription", (default_subscription_model(),)),
    ],
)
async def test_client_missing_token(
    client: toadr3.ToadrClient, method_name: str, method_args: tuple[BaseModel]
) -> None:
    client = toadr3.ToadrClient(
        vtn_url="vtn_url",
        oauth_config=None,
        session=client.client_session,
    )

    msg = "Forbidden 403 - Invalid or missing access token"
    with pytest.raises(toadr3.ToadrError, match=msg):
        _ = await getattr(client, method_name)(*method_args)


@pytest.mark.parametrize(
    ("method_name", "method_args"),
    [
        ("get_programs", ()),
        ("get_events", ()),
        ("get_reports", ()),
        ("get_subscriptions", ()),
    ],
)
async def test_client_result_is_not_a_list(
    client: toadr3.ToadrClient, method_name: str, method_args: tuple[BaseModel]
) -> None:
    custom_headers = {"X-result-type": "dict"}
    msg = "Expected result to be a list"
    with pytest.raises(ValueError, match=msg):
        _ = await getattr(client, method_name)(*method_args, custom_headers=custom_headers)
