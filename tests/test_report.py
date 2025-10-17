import datetime

import pytest
from pydantic import ValidationError
from testdata import create_event, create_report

from toadr3.models import Event, Interval, Report, ReportData, ValuesMap

UTC = datetime.timezone.utc


def test_report() -> None:
    report = Report.model_validate(create_report())

    assert report.id == "19586"
    assert report.created == datetime.datetime(2024, 9, 12, 8, 45, 56, 472000, tzinfo=UTC)
    assert report.modified == datetime.datetime(2024, 9, 12, 8, 46, 56, 472000, tzinfo=UTC)
    assert report.program_id == "1"
    assert report.event_id == "86"
    assert report.client_name == "YAC"
    assert report.report_name == "Test Report"

    assert report.payload_descriptors is not None
    assert len(report.payload_descriptors) == 1
    payload_descriptor = report.payload_descriptors[0]
    assert payload_descriptor.payload_type == "POWER_LIMIT_ACKNOWLEDGEMENT"

    # ReportData
    assert len(report.resources) == 1
    resource = report.resources[0]
    assert isinstance(resource, ReportData)
    assert resource.resource_name == "121"

    assert len(resource.intervals) == 1
    interval = resource.intervals[0]
    assert isinstance(interval, Interval)
    assert interval.id == 0
    assert interval.payloads == [ValuesMap(type="POWER_LIMIT_ACKNOWLEDGEMENT", values=[True])]
    assert not interval.has_interval_period()

    assert resource.interval_period is not None
    assert resource.interval_period.start == datetime.datetime(2024, 8, 12, 12, 15, tzinfo=UTC)
    assert resource.interval_period.duration == datetime.timedelta(minutes=15)


def test_report_default() -> None:
    default_report = {
        "programID": "9",
        "eventID": "67",
        "clientName": "TestYAC",
        "resources": [],
    }
    report = Report.model_validate(default_report)

    assert report.id is None
    assert report.created is None
    assert report.modified is None
    assert report.program_id == "9"
    assert report.event_id == "67"
    assert report.client_name == "TestYAC"
    assert report.report_name is None
    assert report.payload_descriptors is None
    assert report.resources == []


def test_report_exception_program_id() -> None:
    with pytest.raises(ValidationError):
        Report.model_validate({"eventID": "67", "clientName": "TestYAC"})


def test_report_exception_event_id() -> None:
    with pytest.raises(ValidationError):
        Report.model_validate({"programID": "9", "clientName": "TestYAC"})


def test_report_exception_client_name() -> None:
    with pytest.raises(ValidationError):
        Report.model_validate({"programID": "9", "eventID": "67"})


def test_report_exception_resources() -> None:
    with pytest.raises(ValidationError):
        Report.model_validate({"programID": "9", "eventID": "67", "clientName": "TestYAC"})


def test_report_create_report() -> None:
    event = Event.model_validate(create_event())
    report = Report.create_report(
        event, "TestClient", "POWER_LIMIT_ACKNOWLEDGEMENT", ["34"], report_name="Test Report"
    )

    assert report.client_name == "TestClient"
    assert report.report_name == "Test Report"

    assert report.event_id == "37"
    assert report.program_id == "69"

    assert report.payload_descriptors is not None
    assert report.payload_descriptors[0].payload_type == "POWER_LIMIT_ACKNOWLEDGEMENT"

    assert report.resources[0].resource_name == "1211"

    assert report.resources[0].intervals[0].id == 0
    assert report.resources[0].intervals[0].payloads == [
        ValuesMap(type="POWER_LIMIT_ACKNOWLEDGEMENT", values=["34"])
    ]

    assert event.interval_period is not None
    assert report.resources[0].interval_period is not None
    assert report.resources[0].interval_period.start == event.interval_period.start
    assert report.resources[0].interval_period.duration == event.interval_period.duration


@pytest.fixture
def event() -> Event:
    return Event.model_validate(create_event())


def test_report_create_report_error_no_client_name(event: Event) -> None:
    for client_name in [None, True, False, "", []]:  # type: ignore[var-annotated]
        with pytest.raises(ValidationError):
            Report.create_report(event, client_name, "POWER_LIMIT_ACKNOWLEDGEMENT", ["1"])  # type: ignore[arg-type]


def test_report_create_report_error_no_report_type(event: Event) -> None:
    for report_type in [None, True, False, "", []]:  # type: ignore[var-annotated]
        with pytest.raises(ValueError, match="report_type is required"):
            Report.create_report(event, "TestClient", report_type, ["1"])  # type: ignore[arg-type]


def test_report_create_report_no_targets(event: Event) -> None:
    event.targets = None
    with pytest.raises(ValueError, match="event does not have any targets"):
        Report.create_report(event, "TestClient", "POWER_LIMIT_ACKNOWLEDGEMENT", ["1"])

    event.targets = []
    with pytest.raises(ValueError, match="event does not have any targets"):
        Report.create_report(event, "TestClient", "POWER_LIMIT_ACKNOWLEDGEMENT", ["1"])


def test_report_create_report_error_no_report_values(event: Event) -> None:
    for report_values in [None, True, False, "", "abc", []]:  # type: ignore[var-annotated]
        with pytest.raises(ValueError, match="report_values is required"):
            Report.create_report(event, "TestClient", "POWER_LIMIT_ACKNOWLEDGEMENT", report_values)  # type: ignore[arg-type]


def test_report_create_report_error_missing_event_values(event: Event) -> None:
    event.report_descriptors = []
    with pytest.raises(ValueError, match="event does not have any report_descriptors"):
        Report.create_report(event, "TestClient", "POWER_LIMIT_ACKNOWLEDGEMENT", ["1"])

    assert event.targets is not None
    event.targets.pop(0)  # Remove RESOURCE_NAME target
    with pytest.raises(ValueError, match="event does not have a target for type RESOURCE_NAME"):
        Report.create_report(event, "TestClient", "POWER_LIMIT_ACKNOWLEDGEMENT", ["1"])
