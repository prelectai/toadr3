import datetime

import pytest

from toadr3 import IntervalPeriod, SchemaException

td = datetime.timedelta


def interval_period(start: str, duration: str, randomize_start: str) -> IntervalPeriod:
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

    return IntervalPeriod(data)


def test_interval_periods():
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

    with pytest.raises(SchemaException):
        interval_period(None, "PT1H", "PT30M")

    ip = interval_period("2024-09-02T06:12:24Z", "PT17M", "PT37.02S")
    assert str(ip) == "2024-09-02 06:12:24+00:00 - 2024-09-02 06:29:24+00:00 (± 0:00:37.020000)"
