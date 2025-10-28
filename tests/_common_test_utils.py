from aiohttp import web

from toadr3.models import Problem


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
            detail="Invalid or missing access token",
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
