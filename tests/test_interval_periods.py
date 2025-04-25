import datetime

import pytest
from pydantic import ValidationError

import toadr3
from toadr3.models import IntervalPeriod

td = datetime.timedelta


def interval_period(
    start: str | None, duration: str | None, randomize_start: str | None
) -> IntervalPeriod:
    # This function is used to create an IntervalPeriod object from the given data.
    # Setting any value to None will remove it from the data dictionary.
    data = {
        "start": start,
        "duration": duration,
        "randomizeStart": randomize_start,
    }
    if start is None:
        del data["start"]

    if duration is None:
        del data["duration"]

    if randomize_start is None:
        del data["randomizeStart"]

    return IntervalPeriod.model_validate(data)


def test_interval_periods() -> None:
    ip = interval_period("2021-01-01T00:00:00Z", "PT1H", "PT30M")

    assert ip.start == datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
    assert ip.duration == td(hours=1)
    assert ip.randomize_start == td(minutes=30)

    ip = interval_period("2021-01-01T00:00:00Z", "PT1H", None)
    assert ip.randomize_start == td(seconds=0)

    ip = interval_period("2021-01-01T00:00:00Z", None, "PT30M")
    assert ip.duration == td(seconds=0)

    ip = interval_period("2021-01-01T00:00:00Z", None, None)
    assert ip.duration == td(seconds=0)
    assert ip.randomize_start == td(seconds=0)

    with pytest.raises(ValidationError):
        interval_period(None, "PT1H", "PT30M")

    ip = interval_period("2024-09-02T06:12:24Z", "PT17M", "PT37.02S")
    assert str(ip) == "2024-09-02 06:12:24+00:00 - 2024-09-02 06:29:24+00:00 (± 0:00:37.020000)"


def test_interval_period_to_json() -> None:
    data = {
        "start": "2024-09-24T01:02:03Z",
        "duration": "P1DT2H",
        "randomizeStart": "PT5M",
    }
    ip = IntervalPeriod.model_validate(data)

    result = ip.model_dump_json()
    assert result == (
        '{"start":"2024-09-24T01:02:03Z","duration":"P1DT2H","randomizeStart":"PT5M"}'
    )

    # randomizeStart is not set
    data.pop("randomizeStart")
    ip = IntervalPeriod.model_validate(data)

    result = ip.model_dump_json()
    assert result == '{"start":"2024-09-24T01:02:03Z","duration":"P1DT2H","randomizeStart":"PT0S"}'

    result = ip.model_dump_json(exclude_defaults=True)
    assert result == '{"start":"2024-09-24T01:02:03Z","duration":"P1DT2H"}'


def test_interval_periods_sub_second_precision_in_json() -> None:
    """Test that the IntervalPeriod model can handle sub-second precision."""
    ip = interval_period("2024-09-24T01:02:03.123456Z", "PT1H", "PT30M")
    assert ip.start == datetime.datetime(2024, 9, 24, 1, 2, 3, 123456, tzinfo=datetime.timezone.utc)
    assert ip.duration == td(hours=1)
    assert ip.randomize_start == td(minutes=30)

    result = ip.model_dump_json()
    assert result == (
        '{"start":"2024-09-24T01:02:03.123456Z","duration":"PT1H","randomizeStart":"PT30M"}'
    )


def test_interval_periods_with_non_traditional_values() -> None:
    # by default P9999Y is not allowed
    data = '{"start":"2024-09-24","duration":"P9999Y"}'
    with pytest.raises(ValidationError):
        toadr3.models.IntervalPeriod.model_validate_json(data)

    # check that P9999Y returns approximately 9999 years
    ip = toadr3.models.IntervalPeriod.model_validate_json(
        data, context={"allow_P9999Y_duration": True}
    )
    ip.duration = datetime.timedelta(days=365 * 9999)

    # default for 0000-00-00 is to cause a ValidationError
    data = '{"start":"0000-00-00"}'
    with pytest.raises(ValidationError):
        toadr3.models.IntervalPeriod.model_validate_json(data)

    # check that 0000-00-00 is handled correctly
    ip = toadr3.models.IntervalPeriod.model_validate_json(
        data, context={"0000-00-00": datetime.datetime(2024, 9, 24, tzinfo=datetime.timezone.utc)}
    )
    assert ip.start == datetime.datetime(2024, 9, 24, tzinfo=datetime.timezone.utc)

    # The default value for 0000-00-00 is not a datetime
    with pytest.raises(ValidationError):
        toadr3.models.IntervalPeriod.model_validate_json(data, context={"0000-00-00": "???"})
