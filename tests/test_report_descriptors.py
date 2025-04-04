import pytest
from pydantic import ValidationError

from toadr3.models import ReportDescriptor, ValuesMap


def test_report_descriptors() -> None:
    data = """
        {
            "payloadType": "POWER_LIMIT_ACKNOWLEDGEMENT",
            "readingType": "DIRECT_READ",
            "units": "KW",
            "targets": [{"type": "A", "values": [1, 2, 3]}],
            "aggregate": true,
            "startInterval": 0,
            "numIntervals": 2,
            "historical": false,
            "frequency": 4,
            "repeat": -1
        }
        """

    report_descriptor = ReportDescriptor.model_validate_json(data)

    assert report_descriptor.payload_type == "POWER_LIMIT_ACKNOWLEDGEMENT"
    assert report_descriptor.reading_type == "DIRECT_READ"
    assert report_descriptor.units == "KW"
    assert report_descriptor.targets == [ValuesMap(type="A", values=[1, 2, 3])]
    assert report_descriptor.aggregate is True
    assert report_descriptor.start_interval == 0
    assert report_descriptor.num_intervals == 2
    assert report_descriptor.historical is False
    assert report_descriptor.frequency == 4
    assert report_descriptor.repeat == -1


def test_report_descriptors_defaults() -> None:
    data = """
        {
            "payloadType": "POWER_LIMIT_ACKNOWLEDGEMENT"
        }
        """

    report_descriptor = ReportDescriptor.model_validate_json(data)

    assert report_descriptor.payload_type == "POWER_LIMIT_ACKNOWLEDGEMENT"
    assert report_descriptor.reading_type is None
    assert report_descriptor.units is None
    assert report_descriptor.targets is None
    assert report_descriptor.aggregate is False
    assert report_descriptor.start_interval == -1
    assert report_descriptor.num_intervals == -1
    assert report_descriptor.historical is True
    assert report_descriptor.frequency == -1
    assert report_descriptor.repeat == 1


def test_report_descriptors_exception_missing_payload_type() -> None:
    data = """
        {
            "readingType": "DIRECT_READ",
            "units": "KW"
        }
        """

    with pytest.raises(ValidationError):
        ReportDescriptor.model_validate_json(data)
