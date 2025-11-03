from typing import Any

from toadr3.models import Event, ObjectType, OperationType, Program, Report, Subscription


def create_event(**kwargs: str | int) -> dict[str, Any]:
    event: dict[str, Any] = {
        "id": "37",
        "createdDateTime": "2024-08-15T08:52:55.578Z",
        "modificationDateTime": "2024-08-15T08:53:41.127Z",
        "objectType": "EVENT",
        "programID": "69",
        "eventName": "powerLimit",
        "targets": [
            {"type": "RESOURCE_NAME", "values": [1211]},
            {"type": "ORGANIZATION_ID", "values": ["1337"]},
        ],
        "reportDescriptors": [
            {
                "payloadType": "POWER_LIMIT_ACKNOWLEDGEMENT",
                "aggregate": False,
                "startInterval": 0,
                "numIntervals": -1,
                "historical": False,
                "frequency": -1,
                "repeat": 1,
                "targets": [],
            }
        ],
        "payloadDescriptors": [
            {
                "payloadType": "CONSUMPTION_POWER_LIMIT",
                "units": "KW",
                "objectType": "EVENT_PAYLOAD_DESCRIPTOR",
            }
        ],
        "intervalPeriod": {
            "start": "2024-08-15T10:00:00.000Z",
            "duration": "PT15M",
            "randomizeStart": "PT0S",
        },
        "intervals": [
            {"id": 0, "payloads": [{"type": "CONSUMPTION_POWER_LIMIT", "values": [1000]}]}
        ],
    }
    for key, value in kwargs.items():
        if key in event:
            event[key] = value
        # hack to set the resource name
        if key == "resource_name":
            event["targets"][0]["values"] = [value]
    return event


def create_events() -> list[dict[str, Any]]:
    return [
        create_event(id="37", programID="34", eventName="testEvent", resource_name="1211"),
        create_event(id="38", programID="35", eventName="testEvent", resource_name="1212"),
        create_event(id="39", programID="34", eventName="powerLimit", resource_name="1213"),
        create_event(id="40", programID="35", eventName="powerLimit", resource_name="1211"),
        create_event(id="41", programID="34", eventName="powerLimit", resource_name="1212"),
    ]


def create_report(**kwargs: str | int) -> dict[str, Any]:
    report: dict[str, Any] = {
        "id": "19586",
        "createdDateTime": "2024-09-12T08:45:56.472Z",
        "modificationDateTime": "2024-09-12T08:46:56.472Z",
        "objectType": "REPORT",
        "programID": "1",
        "eventID": "86",
        "clientName": "YAC",
        "reportName": "Test Report",
        "payloadDescriptors": [
            {
                "objectType": "REPORT_PAYLOAD_DESCRIPTOR",
                "payloadType": "POWER_LIMIT_ACKNOWLEDGEMENT",
            }
        ],
        "resources": [
            {
                "resourceName": "121",
                "intervals": [
                    {
                        "id": 0,
                        "payloads": [
                            {
                                "type": "POWER_LIMIT_ACKNOWLEDGEMENT",
                                "values": [True],
                            }
                        ],
                    }
                ],
                "intervalPeriod": {"start": "2024-08-12T12:15:00.000Z", "duration": "PT15M"},
            }
        ],
    }
    for key, value in kwargs.items():
        if key in report:
            report[key] = value
    return report


def create_reports() -> list[dict[str, Any]]:
    """Create a list of reports for testing."""
    return [
        create_report(id="99", programID="1", eventID="86", clientName="YAC"),
        create_report(id="100", programID="1", eventID="99", clientName="YAC"),
        create_report(id="101", programID="1", eventID="100", clientName="YAC"),
        create_report(id="102", programID="1", eventID="101", clientName="NAC"),
        create_report(id="103", programID="3", eventID="102", clientName="YAC"),
        create_report(id="104", programID="3", eventID="103", clientName="YAC"),
        create_report(id="105", programID="3", eventID="104", clientName="NAC"),
    ]


def create_program(pid: str, program_name: str, program_long_name: str) -> dict[str, Any]:
    return {
        "id": f"{pid}",
        "createdDateTime": "2025-08-21T07:13:00Z",
        "modificationDateTime": "2025-08-23T08:10:00Z",
        "programName": f"{program_name}",
        "programLongName": f"{program_long_name}",
    }


def create_programs() -> list[dict[str, Any]]:
    return [
        create_program("0", "HB", "Heartbeat"),
        create_program("1", "DR1", "Demand Response 1"),
        create_program("2", "DR2", "Demand Response 2"),
    ]


def create_subscription(sid: str, pid: str, client_name: str = "YAC") -> dict[str, Any]:
    return {
        "id": f"{sid}",
        "createdDateTime": "2025-08-21T07:13:00Z",
        "modificationDateTime": "2025-08-23T08:10:00Z",
        "objectType": "SUBSCRIPTION",
        "clientName": f"{client_name}",
        "programID": f"{pid}",
        "objectOperations": [
            {
                "objects": [ObjectType.EVENT],
                "operations": [OperationType.POST],
                "callbackUrl": "url://callback",
            },
            {
                "objects": [ObjectType.PROGRAM, ObjectType.REPORT],
                "operations": [OperationType.PUT, OperationType.DELETE],
                "callback_url": "url://callback2",
                "bearer_token": "token",
            },
        ],
        "targets": [{"type": "VEN", "values": ["venId"]}],
    }


def create_subscriptions() -> list[dict[str, Any]]:
    exception = create_subscription("7", "5", client_name="NAC")
    exception["objectOperations"] = [
        {
            "objects": [ObjectType.SUBSCRIPTION],
            "operations": [OperationType.POST],
            "callbackUrl": "url://callback3",
        },
    ]
    return [
        create_subscription("2", "5"),
        create_subscription("3", "6"),
        create_subscription("4", "5"),
        exception,
    ]


# The following are default data dictionaries for creating minimal models
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


def default_event_model() -> Event:
    return Event.model_validate(default_event())


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


def default_report_model() -> Report:
    return Report.model_validate(default_report())


def default_program() -> dict[str, Any]:
    return {
        "programName": "pname",
    }


def default_program_model() -> Program:
    return Program.model_validate(default_program())


def default_subscription() -> dict[str, Any]:
    """Create a data for a Subscription model with minimal required data."""
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


def default_subscription_model() -> Subscription:
    """Create a default Subscription model with minimal required data."""
    return Subscription.model_validate(default_subscription())
