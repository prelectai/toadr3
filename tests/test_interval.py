import datetime
import json

import pytest
from pydantic import ValidationError

from toadr3.models import Interval, ValuesMap


def test_interval() -> None:
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

    interval = Interval.model_validate(data)

    assert interval.id == 0
    assert interval.has_interval_period() is False
    assert interval.interval_period is None
    assert len(interval.payloads) == 1
    assert interval.payloads == [ValuesMap(type="CONSUMPTION_POWER_LIMIT", values=[1000])]


def test_interval_with_interval_period() -> None:
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

    interval = Interval.model_validate(data)

    assert interval.id == 9
    assert interval.has_interval_period() is True
    expected_start_time = datetime.datetime(2024, 8, 15, 10, tzinfo=datetime.timezone.utc)
    assert interval.interval_period is not None
    assert interval.interval_period.start == expected_start_time
    assert interval.interval_period.duration == datetime.timedelta(minutes=15)
    assert interval.interval_period.randomize_start == datetime.timedelta(seconds=0)
    assert len(interval.payloads) == 1
    assert interval.payloads == [ValuesMap(type="CONSUMPTION_POWER_LIMIT", values=[6969])]


def test_interval_with_non_standard_duration() -> None:
    data = """
        {
            "id": 9,
            "payloads": [
                    {"type": "CONSUMPTION_POWER_LIMIT", "values": [6969]}
                ],
            "intervalPeriod": {
                "start": "2024-08-15T10:00:00.000Z",
                "duration": "P9999Y"
            }
        }
        """

    interval = Interval.model_validate_json(data, context={"allow_P9999Y_duration": True})
    assert interval.interval_period is not None
    assert interval.interval_period.duration == datetime.timedelta(days=365 * 9999)


def test_interval_with_non_standard_start_datetime() -> None:
    data = """
        {
            "id": 9,
            "payloads": [
                    {"type": "CONSUMPTION_POWER_LIMIT", "values": [6969]}
                ],
            "intervalPeriod": {
                "start": "0000-00-00"
            }
        }
        """

    default_value = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
    interval = Interval.model_validate_json(data, context={"0000-00-00": default_value})
    assert interval.interval_period is not None
    assert interval.interval_period.start == default_value


def test_interval_exception_missing_id() -> None:
    data = json.loads(
        """
        {
            "payloads": [
                    {"type": "CONSUMPTION_POWER_LIMIT", "values": [1000]}
                ]
        }
        """
    )

    with pytest.raises(ValidationError):
        Interval.model_validate(data)


def test_interval_exception_missing_payloads() -> None:
    data = json.loads(
        """
        {
            "id": 0
        }
        """
    )

    with pytest.raises(ValidationError):
        Interval.model_validate(data)


def test_interval_to_json() -> None:
    json_data = (
        '{"id":9,'
        '"intervalPeriod":{'
        '"start":"2024-08-15T10:00:00.001000Z",'
        '"duration":"PT15M",'
        '"randomizeStart":"PT5S"},'
        '"payloads":[{"type":"CONSUMPTION_POWER_LIMIT","values":[34,35]}]'
        "}"
    )

    interval = Interval.model_validate_json(json_data)

    result = interval.model_dump_json()
    assert result == json_data
