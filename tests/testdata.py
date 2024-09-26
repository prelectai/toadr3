from typing import Any


def create_event(**kwargs: str | int) -> dict[str, Any]:
    event = {
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
    report = {
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
