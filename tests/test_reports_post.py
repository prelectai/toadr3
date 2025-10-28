import datetime

import pytest
from aiohttp import ClientSession
from testdata import create_report

from toadr3 import AccessToken, ToadrError, post_report
from toadr3.models import Report


async def test_post_report_required() -> None:
    msg = "report is required"
    with pytest.raises(ValueError, match=msg):
        _ = await post_report(None, "", None, None)  # type: ignore[arg-type]


async def test_post_report_forbidden(session: ClientSession) -> None:
    report = Report.model_validate(create_report())
    with pytest.raises(ToadrError) as exc_info:
        _ = await post_report(session, "", None, report)

    assert exc_info.value.message == "Forbidden"


async def test_post_report_conflict(session: ClientSession, token: AccessToken) -> None:
    data = create_report()
    data["eventID"] = "35"
    report = Report.model_validate(data)

    msg = "Conflict - The report already exists"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_report(session, "", token, report)


async def test_post_report(session: ClientSession, token: AccessToken) -> None:
    report = Report.model_validate(create_report())
    result = await post_report(session, "", token, report)

    assert result.id == "123"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")


async def test_post_report_custom_header(session: ClientSession, token: AccessToken) -> None:
    report = Report.model_validate(create_report())
    result = await post_report(
        session, "", token, report, custom_headers={"X-Custom-Header": "CustomValue"}
    )

    assert result.id == "123"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")


async def test_post_report_invalid_custom_header(
    session: ClientSession, token: AccessToken
) -> None:
    report = Report.model_validate(create_report())

    msg = "Bad Request - Invalid value for X-Custom-Header: InvalidValue"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_report(
            session, "", token, report, custom_headers={"X-Custom-Header": "InvalidValue"}
        )


async def test_post_report_is_none(session: ClientSession, token: AccessToken) -> None:
    with pytest.raises(ValueError, match="report is required"):
        _ = await post_report(session, "", token, None)  # type: ignore[arg-type]
