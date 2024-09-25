import datetime
import json

from testdata import create_event, create_report

import toadr3


def test_json_encoder():
    data = {
        "datetime": datetime.datetime(2024, 9, 24, 1, 2, 3, tzinfo=datetime.timezone.utc),
        "timedelta": datetime.timedelta(days=1, hours=2),
    }

    result = toadr3.ToadrJSONEncoder().encode(data)
    assert result == '{"datetime": "2024-09-24T01:02:03+00:00", "timedelta": "P1DT2H"}'
    assert result == toadr3.toadr_json_serializer(data)


def test_json_encoder_interval_period():
    data = {
        "start": "2024-09-24T01:02:03+00:00",
        "duration": "P1DT2H",
        "randomizeStart": "PT5M",
    }
    ip = toadr3.IntervalPeriod(data)

    result = toadr3.ToadrJSONEncoder().encode(ip)
    assert result == (
        '{"start": "2024-09-24T01:02:03+00:00", "duration": "P1DT2H", "randomizeStart": "PT5M"}'
    )

    # randomizeStart is not set
    data.pop("randomizeStart")
    ip = toadr3.IntervalPeriod(data)

    result = toadr3.ToadrJSONEncoder().encode(ip)
    assert result == '{"start": "2024-09-24T01:02:03+00:00", "duration": "P1DT2H"}'


def test_json_encoder_interval():
    json_data = (
        '{"id": 9, "payloads": [{"type": "CONSUMPTION_POWER_LIMIT", "values": [34, 35]}], '
        '"intervalPeriod": {"start": "2024-08-15T10:00:00.000Z", '
        '"duration": "PT15M", "randomizeStart": "PT5S"}}'
    )

    interval = toadr3.Interval(json.loads(json_data))

    result = toadr3.ToadrJSONEncoder().encode(interval)
    assert result == json_data.replace(".000Z", "+00:00")


def test_json_encoder_report():
    data = create_report()

    report = toadr3.Report(data)

    result = toadr3.ToadrJSONEncoder().encode(report)
    result = json.loads(result)

    # we encode the output of isoformat differently than the input
    data["createdDateTime"] = "2024-09-12T08:45:56.472000+00:00"
    data["modificationDateTime"] = "2024-09-12T08:46:56.472000+00:00"
    data["resources"][0]["intervalPeriod"]["start"] = "2024-08-12T12:15:00+00:00"
    assert result == data


def test_json_encoder_event():
    data = create_event()

    event = toadr3.Event(data)

    result = toadr3.ToadrJSONEncoder().encode(event)
    result = json.loads(result)

    data["createdDateTime"] = "2024-08-15T08:52:55.578000+00:00"
    data["modificationDateTime"] = "2024-08-15T08:53:41.127000+00:00"
    data["intervalPeriod"]["start"] = "2024-08-15T10:00:00+00:00"

    # we do not serialize if duration is 0
    del data["intervalPeriod"]["randomizeStart"]

    # we serialize default values for the reportDescriptors
    data["reportDescriptors"][0]["aggregate"] = False
    data["reportDescriptors"][0]["historical"] = False
    data["reportDescriptors"][0]["startInterval"] = 0
    data["reportDescriptors"][0]["targets"] = []

    assert result == data
