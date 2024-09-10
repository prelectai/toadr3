from typing import Any


def create_event(**kwargs: dict[str, Any]) -> dict:
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
    return event
