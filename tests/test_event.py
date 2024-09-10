import datetime

import pytest
from testdata import create_event

import toadr3

UTC = datetime.timezone.utc


def test_event():
    event = toadr3.Event(create_event())

    assert event.id == "37"
    assert event.created == datetime.datetime(2024, 8, 15, 8, 52, 55, 578000, tzinfo=UTC)
    assert event.modified == datetime.datetime(2024, 8, 15, 8, 53, 41, 127000, tzinfo=UTC)
    assert event.program_id == "69"
    assert event.event_name == "powerLimit"
    assert event.priority is None

    assert len(event.targets) == 2
    assert event.targets == {"RESOURCE_NAME": [1211], "ORGANIZATION_ID": ["1337"]}

    assert len(event.report_descriptors) == 1
    report_descriptor = event.report_descriptors[0]
    assert report_descriptor.payload_type == "POWER_LIMIT_ACKNOWLEDGEMENT"

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
    assert interval.payloads == {"CONSUMPTION_POWER_LIMIT": [1000]}


def test_event_defaults():
    event = toadr3.Event(
        {
            "objectType": "EVENT",
            "programID": "69",
            "intervals": [
                {"id": 0, "payloads": [{"type": "CONSUMPTION_POWER_LIMIT", "values": [1000]}]}
            ],
        }
    )

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
    assert interval.payloads == {"CONSUMPTION_POWER_LIMIT": [1000]}


def test_event_exception_program_id():
    with pytest.raises(toadr3.SchemaException) as e:
        toadr3.Event({"objectType": "EVENT", "intervals": [{"id": 0, "payloads": []}]})
    assert str(e.value) == "Missing 'programID' in event schema."


def test_event_exception_intervals():
    with pytest.raises(toadr3.SchemaException) as e:
        toadr3.Event({"objectType": "EVENT", "programID": "69"})
    assert str(e.value) == "Missing 'intervals' in event schema."
