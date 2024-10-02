import datetime

import pytest
from testdata import create_event, create_report

import toadr3

UTC = datetime.timezone.utc


def test_report():
    report = toadr3.Report(create_report())

    assert report.id == "19586"
    assert report.created == datetime.datetime(2024, 9, 12, 8, 45, 56, 472000, tzinfo=UTC)
    assert report.modified == datetime.datetime(2024, 9, 12, 8, 46, 56, 472000, tzinfo=UTC)
    assert report.program_id == "1"
    assert report.event_id == "86"
    assert report.client_name == "YAC"
    assert report.report_name == "Test Report"

    assert len(report.payload_descriptors) == 1
    payload_descriptor = report.payload_descriptors[0]
    assert payload_descriptor.payload_type == "POWER_LIMIT_ACKNOWLEDGEMENT"

    # ReportData
    assert len(report.resources) == 1
    resource = report.resources[0]
    assert isinstance(resource, toadr3.ReportData)
    assert resource.resource_name == "121"

    assert len(resource.intervals) == 1
    interval = resource.intervals[0]
    assert isinstance(interval, toadr3.Interval)
    assert interval.id == 0
    assert interval.payloads == {"POWER_LIMIT_ACKNOWLEDGEMENT": [True]}
    assert not interval.has_interval_period()

    assert resource.interval_period.start == datetime.datetime(2024, 8, 12, 12, 15, tzinfo=UTC)
    assert resource.interval_period.duration == datetime.timedelta(minutes=15)


def test_report_default():
    default_report = {
        "programID": "9",
        "eventID": "67",
        "clientName": "TestYAC",
        "resources": [],
    }
    report = toadr3.Report(default_report)

    assert report.id is None
    assert report.created is None
    assert report.modified is None
    assert report.program_id == "9"
    assert report.event_id == "67"
    assert report.client_name == "TestYAC"
    assert report.report_name is None
    assert report.payload_descriptors is None
    assert report.resources == []


def test_report_exception_program_id():
    with pytest.raises(toadr3.SchemaError) as e:
        toadr3.Report({"eventID": "67", "clientName": "TestYAC"})
    assert str(e.value) == "Missing 'programID' in report schema."


def test_report_exception_event_id():
    with pytest.raises(toadr3.SchemaError) as e:
        toadr3.Report({"programID": "9", "clientName": "TestYAC"})
    assert str(e.value) == "Missing 'eventID' in report schema."


def test_report_exception_client_name():
    with pytest.raises(toadr3.SchemaError) as e:
        toadr3.Report({"programID": "9", "eventID": "67"})
    assert str(e.value) == "Missing 'clientName' in report schema."


def test_report_exception_resources():
    with pytest.raises(toadr3.SchemaError) as e:
        toadr3.Report({"programID": "9", "eventID": "67", "clientName": "TestYAC"})
    assert str(e.value) == "Missing 'resources' in report schema."


def test_report_create_report():
    event = toadr3.Event(create_event())
    report = toadr3.create_report(
        event, "TestClient", "POWER_LIMIT_ACKNOWLEDGEMENT", ["34"], report_name="Test Report"
    )

    assert report.client_name == "TestClient"
    assert report.report_name == "Test Report"

    assert report.event_id == "37"
    assert report.program_id == "69"

    assert report.payload_descriptors[0].payload_type == "POWER_LIMIT_ACKNOWLEDGEMENT"

    assert report.resources[0].resource_name == 1211

    assert report.resources[0].intervals[0].id == 0
    assert report.resources[0].intervals[0].payloads == {"POWER_LIMIT_ACKNOWLEDGEMENT": ["34"]}

    assert report.resources[0].interval_period.start == event.interval_period.start
    assert report.resources[0].interval_period.duration == event.interval_period.duration


@pytest.fixture
def event():
    return toadr3.Event(create_event())


def test_report_create_report_error_no_client_name(event: toadr3.Event):
    for client_name in [None, True, False, "", []]:
        with pytest.raises(ValueError, match="client_name is required."):
            toadr3.create_report(event, client_name, "TYPE", ["1"])


def test_report_create_report_error_no_report_type(event: toadr3.Event):
    for report_type in [None, True, False, "", []]:
        with pytest.raises(ValueError, match="report_type is required."):
            toadr3.create_report(event, "TestClient", report_type, ["1"])


def test_report_create_report_error_no_report_values(event: toadr3.Event):
    for report_values in [None, True, False, "", "abc", []]:
        with pytest.raises(ValueError, match="report_values is required."):
            toadr3.create_report(event, "TestClient", "TYPE", report_values)


def test_report_create_report_error_missing_event_values(event: toadr3.Event):
    attributes = [
        ("_id", "an ID"),
        ("_program_id", "a program ID"),
        ("_interval_period", "an interval period"),
    ]
    for attribute, description in attributes:
        old = getattr(event, attribute)
        setattr(event, attribute, None)
        with pytest.raises(ValueError, match=f"event must have {description}."):
            toadr3.create_report(event, "TestClient", "TYPE", ["1"])

        setattr(event, attribute, old)

    event._report_descriptors = []  # noqa: SLF001 (access to a private attribute)
    with pytest.raises(ValueError, match="event does not have any report_descriptors."):
        toadr3.create_report(event, "TestClient", "TYPE", ["1"])

    event.targets.pop("RESOURCE_NAME")
    with pytest.raises(ValueError, match="event does not have a target for RESOURCE_NAME."):
        toadr3.create_report(event, "TestClient", "TYPE", ["1"])
