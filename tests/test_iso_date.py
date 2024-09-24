import datetime

import pytest

from toadr3 import parse_iso8601_duration
from toadr3.iso_date import create_iso8601_duration

td = datetime.timedelta


def check_raises_value_error(duration: str):
    match = f"Invalid ISO 8601 duration: {duration}"
    with pytest.raises(ValueError, match=match):
        print(parse_iso8601_duration(duration))


def test_duration_parse_errors():
    # year not supported
    check_raises_value_error("P1Y")

    # month not supported
    check_raises_value_error("P1M")

    # year and month not supported
    check_raises_value_error("P3Y6M4DT12H30M5S")

    # no fractional part for minutes
    check_raises_value_error("PT1.5M")

    # no fractional part for hours
    check_raises_value_error("PT1.5H")

    # no T before W
    check_raises_value_error("PT1W")

    # no T before D
    check_raises_value_error("PT1D")

    # no duration values
    check_raises_value_error("P")

    # no duration values
    check_raises_value_error("PT")

    # missing duration unit
    check_raises_value_error("P1")

    # missing duration unit
    check_raises_value_error("PT1")

    # missing integer part
    check_raises_value_error("PT.5S")

    # missing fractional part
    check_raises_value_error("PT5.S")


def test_duration_parse():
    assert parse_iso8601_duration("P1W") == td(days=7)
    assert parse_iso8601_duration("P1D") == td(days=1)
    assert parse_iso8601_duration("PT1H") == td(hours=1)
    assert parse_iso8601_duration("PT1M") == td(minutes=1)
    assert parse_iso8601_duration("PT1S") == td(seconds=1)
    assert parse_iso8601_duration("PT0.5S") == td(milliseconds=500)
    assert parse_iso8601_duration("P6DT12H30M5.758S") == td(
        days=6, hours=12, minutes=30, seconds=5, milliseconds=758
    )
    assert parse_iso8601_duration("P1W6DT12H30M5.758S") == td(
        days=13, hours=12, minutes=30, seconds=5, milliseconds=758
    )
    assert parse_iso8601_duration("PT1H1M1S") == td(hours=1, minutes=1, seconds=1)
    assert parse_iso8601_duration("PT1H1M") == td(hours=1, minutes=1)
    assert parse_iso8601_duration("PT1H1S") == td(hours=1, seconds=1)
    assert parse_iso8601_duration("PT1M1S") == td(minutes=1, seconds=1)
    assert parse_iso8601_duration("PT1.5S") == td(seconds=1, milliseconds=500)


def test_duration_parse_negative():
    assert parse_iso8601_duration("P-1D") == td(days=-1)
    assert parse_iso8601_duration("-P1D") == td(days=-1)
    assert parse_iso8601_duration("-P-1D") == td(days=1)

    assert parse_iso8601_duration("P-1W") == td(days=-7)
    assert parse_iso8601_duration("-P1W") == td(days=-7)
    assert parse_iso8601_duration("-P-1W") == td(days=7)

    assert parse_iso8601_duration("P-1W1D") == td(days=-6)
    assert parse_iso8601_duration("-P-1W1D") == td(days=6)
    assert parse_iso8601_duration("P1W-1D") == td(days=6)
    assert parse_iso8601_duration("-P1W-1D") == td(days=-6)

    assert parse_iso8601_duration("PT-1H") == td(hours=-1)
    assert parse_iso8601_duration("-PT1H") == td(hours=-1)
    assert parse_iso8601_duration("-PT-1H") == td(hours=1)

    assert parse_iso8601_duration("PT-1M") == td(minutes=-1)
    assert parse_iso8601_duration("-PT1M") == td(minutes=-1)
    assert parse_iso8601_duration("-PT-1M") == td(minutes=1)

    assert parse_iso8601_duration("PT-1S") == td(seconds=-1)
    assert parse_iso8601_duration("-PT1S") == td(seconds=-1)
    assert parse_iso8601_duration("-PT-1S") == td(seconds=1)

    assert parse_iso8601_duration("PT-0.5S") == td(milliseconds=-500)
    assert parse_iso8601_duration("-PT0.5S") == td(milliseconds=-500)
    assert parse_iso8601_duration("-PT-0.5S") == td(milliseconds=500)

    assert parse_iso8601_duration("PT-1M-1S") == td(minutes=-1, seconds=-1)
    assert parse_iso8601_duration("PT1M-1S") == td(minutes=1, seconds=-1)
    assert parse_iso8601_duration("PT-1M1S") == td(minutes=-1, seconds=1)
    assert parse_iso8601_duration("-PT1M1S") == td(minutes=-1, seconds=-1)
    assert parse_iso8601_duration("-PT-1M1S") == td(minutes=1, seconds=-1)
    assert parse_iso8601_duration("-PT1M-1S") == td(minutes=-1, seconds=1)
    assert parse_iso8601_duration("-PT-1M-1S") == td(minutes=1, seconds=1)

    assert parse_iso8601_duration("PT-1M-0.5S") == td(minutes=-1, milliseconds=-500)
    assert parse_iso8601_duration("PT1M-0.5S") == td(minutes=1, milliseconds=-500)
    assert parse_iso8601_duration("PT-1M0.5S") == td(minutes=-1, milliseconds=500)
    assert parse_iso8601_duration("-PT1M0.5S") == td(minutes=-1, milliseconds=-500)
    assert parse_iso8601_duration("-PT-1M0.5S") == td(minutes=1, milliseconds=-500)
    assert parse_iso8601_duration("-PT1M-0.5S") == td(minutes=-1, milliseconds=500)
    assert parse_iso8601_duration("-PT-1M-0.5S") == td(minutes=1, milliseconds=500)

    assert parse_iso8601_duration("P-1W-1DT-1H-1M-1S") == td(
        days=-8, hours=-1, minutes=-1, seconds=-1
    )
    assert parse_iso8601_duration("-P-1W-1DT-1H-1M-1S") == td(days=8, hours=1, minutes=1, seconds=1)


def test_duration_timedelta_to_duration():
    assert create_iso8601_duration(td(days=7)) == "P1W"
    assert create_iso8601_duration(td(days=-7)) == "-P1W"
    assert create_iso8601_duration(td(days=1)) == "P1D"
    assert create_iso8601_duration(td(days=-1)) == "-P1D"
    assert create_iso8601_duration(td(hours=1)) == "PT1H"
    assert create_iso8601_duration(td(hours=-1)) == "-PT1H"
    assert create_iso8601_duration(td(minutes=1)) == "PT1M"
    assert create_iso8601_duration(td(minutes=-1)) == "-PT1M"
    assert create_iso8601_duration(td(seconds=1)) == "PT1S"
    assert create_iso8601_duration(td(seconds=-1)) == "-PT1S"
    assert create_iso8601_duration(td(milliseconds=500)) == "PT0.5S"
    assert create_iso8601_duration(td(milliseconds=-500)) == "-PT0.5S"
    assert create_iso8601_duration(td(microseconds=1)) == "PT0.000001S"
    assert create_iso8601_duration(td(microseconds=-1)) == "-PT0.000001S"

    assert create_iso8601_duration(td(days=0)) == "PT0S"

    time_delta = td(days=6, hours=12, minutes=30, seconds=5, milliseconds=758)
    assert create_iso8601_duration(time_delta) == "P6DT12H30M5.758S"

    time_delta = td(days=-6, hours=-12, minutes=-30, seconds=-5, milliseconds=-758)
    assert create_iso8601_duration(time_delta) == "-P6DT12H30M5.758S"

    assert create_iso8601_duration(td(hours=-1, minutes=1, seconds=1)) == "-PT58M59S"
