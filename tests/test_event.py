import datetime

import pytest
from pydantic import ValidationError
from testdata import create_event

import toadr3

UTC = datetime.timezone.utc


def test_event() -> None:
    event = toadr3.models.Event.model_validate(create_event())

    assert event.id == "37"
    assert event.created == datetime.datetime(2024, 8, 15, 8, 52, 55, 578000, tzinfo=UTC)
    assert event.modified == datetime.datetime(2024, 8, 15, 8, 53, 41, 127000, tzinfo=UTC)
    assert event.program_id == "69"
    assert event.event_name == "powerLimit"
    assert event.priority is None

    assert event.targets is not None
    assert len(event.targets) == 2
    assert event.targets == [
        toadr3.models.ValuesMap(type="RESOURCE_NAME", values=[1211]),
        toadr3.models.ValuesMap(type="ORGANIZATION_ID", values=["1337"]),
    ]

    assert event.report_descriptors is not None
    assert len(event.report_descriptors) == 1
    report_descriptor = event.report_descriptors[0]
    assert report_descriptor.payload_type == "POWER_LIMIT_ACKNOWLEDGEMENT"

    assert event.payload_descriptors is not None
    assert len(event.payload_descriptors) == 1
    payload_descriptor = event.payload_descriptors[0]
    assert payload_descriptor.payload_type == "CONSUMPTION_POWER_LIMIT"
    assert payload_descriptor.units == "KW"

    assert event.interval_period is not None
    assert event.interval_period.start == datetime.datetime(2024, 8, 15, 10, tzinfo=UTC)
    assert event.interval_period.duration == datetime.timedelta(minutes=15)
    assert event.interval_period.randomize_start == datetime.timedelta(seconds=0)

    assert len(event.intervals) == 1
    interval = event.intervals[0]
    assert not interval.has_interval_period()
    assert interval.id == 0
    assert interval.payloads == [
        toadr3.models.ValuesMap(type="CONSUMPTION_POWER_LIMIT", values=[1000])
    ]


def test_event_defaults() -> None:
    data = {
        "objectType": "EVENT",
        "programID": "69",
        "intervals": [
            {"id": 0, "payloads": [{"type": "CONSUMPTION_POWER_LIMIT", "values": [1000]}]}
        ],
    }
    event = toadr3.models.Event.model_validate(data)

    assert event.id is None
    assert event.created is None
    assert event.modified is None
    assert event.program_id == "69"
    assert event.event_name is None
    assert event.priority is None
    assert event.targets is None
    assert event.report_descriptors is None
    assert event.payload_descriptors is None
    assert event.interval_period is None

    assert len(event.intervals) == 1
    interval = event.intervals[0]
    assert not interval.has_interval_period()
    assert interval.id == 0
    assert interval.payloads == [
        toadr3.models.ValuesMap(type="CONSUMPTION_POWER_LIMIT", values=[1000])
    ]


def test_event_interval_period_start_0000_00_00() -> None:
    data = {
        "objectType": "EVENT",
        "programID": "69",
        "intervalPeriod": {"start": "0000-00-00", "duration": "PT15M", "randomizeStart": "PT0S"},
        "intervals": [
            {"id": 0, "payloads": [{"type": "CONSUMPTION_POWER_LIMIT", "values": [1000]}]}
        ],
    }
    event = toadr3.models.Event.model_validate(data)

    assert event.interval_period is not None
    assert event.interval_period.start == "0000-00-00"
    assert event.interval_period.duration == datetime.timedelta(minutes=15)
    assert event.interval_period.randomize_start == datetime.timedelta(seconds=0)


def test_event_exception_program_id() -> None:
    with pytest.raises(ValidationError):
        toadr3.models.Event.model_validate(
            {"objectType": "EVENT", "intervals": [{"id": 0, "payloads": []}]}
        )


def test_event_exception_intervals() -> None:
    with pytest.raises(ValidationError):
        toadr3.models.Event.model_validate({"objectType": "EVENT", "programID": "69"})
