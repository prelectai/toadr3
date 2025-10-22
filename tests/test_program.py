import datetime

from testdata import create_program

import toadr3

UTC = datetime.timezone.utc


def test_program_defaults() -> None:
    program = toadr3.models.Program(
        program_name="Test Program",
    )

    assert program.id is None
    assert program.created_date_time is None
    assert program.modification_date_time is None
    assert program.object_type == "PROGRAM"
    assert program.program_name == "Test Program"
    assert program.program_long_name is None
    assert program.retailer_name is None
    assert program.retailer_long_name is None
    assert program.program_type is None
    assert program.country is None
    assert program.principal_subdivision is None
    assert program.time_zone_offset == datetime.timedelta(seconds=0)
    assert program.interval_period is None
    assert program.program_descriptions is None
    assert program.binding_events is None
    assert program.local_price is None
    assert program.payload_descriptors is None
    assert program.targets is None


def test_program_sample() -> None:
    sample_1 = create_program("0", "HB", "Heartbeat")

    program = toadr3.models.Program.model_validate(sample_1)

    assert program.id == "0"
    assert program.program_name == "HB"
    assert program.program_long_name == "Heartbeat"
    assert program.created_date_time == datetime.datetime(2025, 8, 21, 7, 13, 0, tzinfo=UTC)
    assert program.modification_date_time == datetime.datetime(2025, 8, 23, 8, 10, 0, tzinfo=UTC)
