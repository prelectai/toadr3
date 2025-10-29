from typing import Any, Protocol

import aiohttp
import pytest
from aiohttp import web

from toadr3 import AccessToken, ToadrClient
from toadr3.models import DocstringBaseModel, Problem


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

    @property
    def __name__(self) -> str:
        """Return the name of the query function."""


async def check_functions_raises(
    function: QueryFunction,
    kwargs: dict[str, Any],
    msg: str,
    client: ToadrClient,
    exception_type: type[Exception],
) -> None:
    """Check that the query function and the equivalent client function is valid."""
    token = await client.token
    with pytest.raises(exception_type, match=msg):
        _ = await function(client.client_session, client.vtn_url, token, **kwargs)

    with pytest.raises(exception_type, match=msg):
        _ = await getattr(client, function.__name__)(**kwargs)


def create_problem_response(title: str, status: int, detail: str) -> web.Response:
    """Create a web.Response with a Problem JSON body."""
    return web.json_response(
        data=Problem(
            title=title,
            status=status,
            detail=detail,
        ),
        status=status,
        dumps=Problem.model_dump_json,
    )


def check_extra_params(x_parity: str | None) -> web.Response | None:
    """Check if the x-parity parameter is valid."""
    if x_parity is not None and x_parity not in ["even", "odd"]:
        return create_problem_response(
            title="Bad Request",
            status=400,
            detail=f"Invalid value for x-parity: {x_parity}",
        )
    return None


def check_custom_header(custom_header: str | None) -> web.Response | None:
    """Check if the custom header is valid."""
    if custom_header is not None and custom_header != "CustomValue":
        return create_problem_response(
            title="Bad Request",
            status=400,
            detail=f"Invalid value for X-Custom-Header: {custom_header}",
        )
    return None


def check_credentials(auth: str | None) -> web.Response | None:
    """Check if the credentials are valid."""
    if auth is None or not auth.startswith("Bearer ") or auth.split(" ")[1] != "token":
        return create_problem_response(
            title="Forbidden",
            status=403,
            detail=f"Invalid or missing access token: '{auth}' != 'token'",
        )
    return None


def filter_items(
    items: list[dict[str, str]], skip: str | None, limit: str | None, x_parity: str | None
) -> list[dict[str, str]]:
    """Filter the items based on skip, limit and x_parity parameters."""
    if skip is not None:
        int_skip = int(skip)
        items = items[int_skip:]

    if limit is not None:
        int_limit = int(limit)
        items = items[:int_limit]

    if x_parity is not None:
        parity = 0 if x_parity == "even" else 1
        items = [item for item in items if int(item["id"]) % 2 == parity]

    return items
