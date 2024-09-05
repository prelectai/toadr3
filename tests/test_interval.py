import datetime
import json

import pytest

from toadr3 import Interval, SchemaException


def test_interval():
    data = json.loads(
        """
        {
            "id": 0,
            "payloads": [
                    {"type": "CONSUMPTION_POWER_LIMIT", "values": [1000]}
                ]
        }
        """
    )

    interval = Interval(data)

    assert interval.id == 0
    assert interval.has_interval_period() is False
    assert interval.interval_period is None
    assert len(interval.payloads) == 1
    assert interval.payloads == {"CONSUMPTION_POWER_LIMIT": [1000]}


def test_interval_with_interval_period():
    data = json.loads(
        """
        {
            "id": 9,
            "payloads": [
                    {"type": "CONSUMPTION_POWER_LIMIT", "values": [6969]}
                ],
            "intervalPeriod": {
                "start": "2024-08-15T10:00:00.000Z",
                "duration": "PT15M",
                "randomizeStart": "PT0S"
            }
        }
        """
    )

    interval = Interval(data)

    assert interval.id == 9
    assert interval.has_interval_period() is True
    expected_start_time = datetime.datetime(2024, 8, 15, 10, tzinfo=datetime.timezone.utc)
    assert interval.interval_period.start == expected_start_time
    assert interval.interval_period.duration == datetime.timedelta(minutes=15)
    assert interval.interval_period.randomize_start == datetime.timedelta(seconds=0)
    assert len(interval.payloads) == 1
    assert interval.payloads == {"CONSUMPTION_POWER_LIMIT": [6969]}


def test_interval_exception_missing_id():
    data = json.loads(
        """
        {
            "payloads": [
                    {"type": "CONSUMPTION_POWER_LIMIT", "values": [1000]}
                ]
        }
        """
    )

    with pytest.raises(SchemaException) as e:
        Interval(data)
    assert str(e.value) == "Missing 'id' in interval schema."


def test_interval_exception_missing_payloads():
    data = json.loads(
        """
        {
            "id": 0
        }
        """
    )

    with pytest.raises(SchemaException) as e:
        Interval(data)
    assert str(e.value) == "Missing 'payloads' in interval schema."
