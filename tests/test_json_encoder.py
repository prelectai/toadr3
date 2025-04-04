import datetime

from testdata import create_event, create_report

import toadr3

from_iso = datetime.datetime.fromisoformat


def test_json_encoder_report() -> None:
    data = create_report()

    report = toadr3.models.Report.model_validate(data)
    result = toadr3.models.Report.model_dump(report, exclude_none=True, exclude_unset=True)

    # for comparison, we expect datetime objects and not strings
    data["createdDateTime"] = from_iso(data["createdDateTime"])
    data["modificationDateTime"] = from_iso(data["modificationDateTime"])
    data["resources"][0]["intervalPeriod"]["duration"] = datetime.timedelta(minutes=15)
    data["resources"][0]["intervalPeriod"]["start"] = from_iso(
        data["resources"][0]["intervalPeriod"]["start"]
    )

    assert result == data


def test_json_encoder_event() -> None:
    data = create_event()

    event = toadr3.models.Event.model_validate(data)
    result = toadr3.models.Event.model_dump(event, exclude_none=True, exclude_unset=True)

    # for comparison, we expect datetime objects and not strings
    data["createdDateTime"] = from_iso(data["createdDateTime"])
    data["modificationDateTime"] = from_iso(data["modificationDateTime"])
    data["intervalPeriod"]["duration"] = datetime.timedelta(minutes=15)
    data["intervalPeriod"]["randomizeStart"] = datetime.timedelta(seconds=0)
    data["intervalPeriod"]["start"] = from_iso(data["intervalPeriod"]["start"])

    assert result == data
