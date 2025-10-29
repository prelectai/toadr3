import datetime

import pytest
from testdata import create_report

from toadr3 import ToadrClient, ToadrError, post_report
from toadr3.models import Report


async def test_post_report_forbidden(client: ToadrClient) -> None:
    mock_client = ToadrClient(client.vtn_url, None, client.client_session)
    session = mock_client.client_session
    token = await mock_client.token
    vtn_url = mock_client.vtn_url

    report = Report.model_validate(create_report())
    msg = "Forbidden"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_report(session, vtn_url, token, report)

    with pytest.raises(ToadrError, match=msg):
        _ = await mock_client.post_report(report)


async def test_post_report_conflict(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    data = create_report()
    data["eventID"] = "35"
    report = Report.model_validate(data)

    msg = "Conflict 409 - The report already exists"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_report(session, vtn_url, token, report)

    with pytest.raises(ToadrError, match=msg):
        _ = await client.post_report(report)


async def test_post_report(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    report = Report.model_validate(create_report())

    result = await post_report(session, vtn_url, token, report)
    assert result.id == "1234"
    assert result.client_name == "YAC"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")

    result = await client.post_report(report)
    assert result.id == "1234"
    assert result.client_name == "YAC"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")


async def test_post_report_custom_header(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    report = Report.model_validate(create_report())

    result = await post_report(
        session, vtn_url, token, report, custom_headers={"X-Custom-Header": "CustomValue"}
    )
    assert result.id == "1234"
    assert result.client_name == "CustomClientName"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")

    result = await client.post_report(report, custom_headers={"X-Custom-Header": "CustomValue"})
    assert result.id == "1234"
    assert result.client_name == "CustomClientName"
    assert result.created == datetime.datetime.fromisoformat("2024-09-30T12:12:34Z")
    assert result.modified == datetime.datetime.fromisoformat("2024-09-30T12:12:35Z")


async def test_post_report_invalid_custom_header(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    report = Report.model_validate(create_report())

    msg = "Bad Request 400 - Invalid value for X-Custom-Header: InvalidValue"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_report(
            session, vtn_url, token, report, custom_headers={"X-Custom-Header": "InvalidValue"}
        )

    with pytest.raises(ToadrError, match=msg):
        _ = await client.post_report(report, custom_headers={"X-Custom-Header": "InvalidValue"})


async def test_post_report_is_none(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    msg = "report is required"
    with pytest.raises(ValueError, match=msg):
        _ = await post_report(None, vtn_url, None, None)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=msg):
        _ = await post_report(session, vtn_url, token, None)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match=msg):
        _ = await client.post_report(None)  # type: ignore[arg-type]


async def test_post_report_unauthorized(client: ToadrClient) -> None:
    session = client.client_session
    token = await client.token
    vtn_url = client.vtn_url

    report = Report.model_validate(create_report())
    report.client_name = "Unauthorized"

    msg = "Unauthorized 401 - You are not authorized to perform this action"
    with pytest.raises(ToadrError, match=msg):
        _ = await post_report(session, vtn_url, token, report)

    with pytest.raises(ToadrError, match=msg):
        _ = await client.post_report(report)
