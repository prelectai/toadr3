import datetime
from typing import Any

import pytest
from pydantic import BaseModel
from testdata import create_event, create_report

from toadr3.models import Event, Program, Report, Subscription

from_iso = datetime.datetime.fromisoformat


def test_json_encoder_report() -> None:
    data = create_report()

    report = Report.model_validate(data)
    result = Report.model_dump(report, exclude_none=True, exclude_unset=True)

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

    event = Event.model_validate(data)
    result = Event.model_dump(event, exclude_none=True, exclude_unset=True)

    # for comparison, we expect datetime objects and not strings
    data["createdDateTime"] = from_iso(data["createdDateTime"])
    data["modificationDateTime"] = from_iso(data["modificationDateTime"])
    data["intervalPeriod"]["duration"] = datetime.timedelta(minutes=15)
    data["intervalPeriod"]["randomizeStart"] = datetime.timedelta(seconds=0)
    data["intervalPeriod"]["start"] = from_iso(data["intervalPeriod"]["start"])

    assert result == data


def default_event() -> dict[str, Any]:
    return {
        "programID": "11",
        "intervals": [
            {
                "id": 1,
                "payloads": [{"type": "type", "values": ["value1"]}],
            }
        ],
    }


def default_report() -> dict[str, Any]:
    return {
        "programID": "11",
        "eventID": "33",
        "clientName": "YAC",
        "resources": [
            {
                "resourceName": "resource1",
                "intervals": [
                    {
                        "id": 1,
                        "payloads": [{"type": "type", "values": ["value1"]}],
                    }
                ],
            }
        ],
    }


def default_program() -> dict[str, Any]:
    return {
        "programName": "pname",
    }


def default_subscription() -> dict[str, Any]:
    return {
        "clientName": "YAC",
        "programID": "11",
        "objectOperations": [
            {
                "objects": ["EVENT"],
                "operations": ["POST"],
                "callbackUrl": "https://example.com/callback",
            }
        ],
    }


@pytest.mark.parametrize(
    ("model_class", "model_data"),
    [
        (Event, default_event()),
        (Report, default_report()),
        (Program, default_program()),
        (Subscription, default_subscription()),
    ],
)
def test_json_encode_as_expected(model_class: type[BaseModel], model_data: dict[str, Any]) -> None:
    # 1. we expect only default values to be part of the final JSON
    # 2. we expect the 'objectType' field to be included in the final JSON
    instance = model_class.model_validate(model_data)
    result = model_class.model_dump(instance, exclude_none=True, exclude_unset=True)

    assert "objectType" not in model_data
    assert "objectType" in result
    assert result["objectType"] == model_class.__name__.upper()

    model_data["objectType"] = model_class.__name__.upper()
    assert result == model_data
