import datetime

import pytest

from toadr3 import parse_iso8601_duration

td = datetime.timedelta


def test_duration_parse_errors():
    with pytest.raises(ValueError):
        # year not supported
        parse_iso8601_duration("P1Y")

    with pytest.raises(ValueError):
        # month not supported
        print(parse_iso8601_duration("P1M"))

    with pytest.raises(ValueError):
        # weeks not supported
        parse_iso8601_duration("P1W")

    with pytest.raises(ValueError):
        # year and month not supported
        parse_iso8601_duration("P3Y6M4DT12H30M5S")

    with pytest.raises(ValueError):
        # no fractional part for minutes
        parse_iso8601_duration("PT1.5M")

    with pytest.raises(ValueError):
        # no fractional part for hours
        parse_iso8601_duration("PT1.5H")

    with pytest.raises(ValueError):
        # no T before D
        parse_iso8601_duration("PT1D")


def test_duration_parse():
    assert parse_iso8601_duration("P1D") == td(days=1)
    assert parse_iso8601_duration("PT1H") == td(hours=1)
    assert parse_iso8601_duration("PT1M") == td(minutes=1)
    assert parse_iso8601_duration("PT1S") == td(seconds=1)
    assert parse_iso8601_duration("PT0.5S") == td(milliseconds=500)
    assert parse_iso8601_duration("P6DT12H30M5.758S") == td(
        days=6, hours=12, minutes=30, seconds=5, milliseconds=758
    )
    assert parse_iso8601_duration("PT1H1M1S") == td(hours=1, minutes=1, seconds=1)
    assert parse_iso8601_duration("PT1H1M") == td(hours=1, minutes=1)
    assert parse_iso8601_duration("PT1H1S") == td(hours=1, seconds=1)
    assert parse_iso8601_duration("PT1M1S") == td(minutes=1, seconds=1)
    assert parse_iso8601_duration("PT1.5S") == td(seconds=1, milliseconds=500)
