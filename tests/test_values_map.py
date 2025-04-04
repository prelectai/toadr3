import pytest
from pydantic import ValidationError

from toadr3.models import Point, ValuesMap


def test_values_map_int() -> None:
    vmdata = '{"type":"RESOURCE_NAME","values":[1211]}'

    vm = ValuesMap.model_validate_json(vmdata)
    assert vm.type == "RESOURCE_NAME"
    assert vm.values == [1211]


def test_values_map_string() -> None:
    vmdata = '{"type":"RESOURCE_NAME","values":["1337"]}'

    vm = ValuesMap.model_validate_json(vmdata)
    assert vm.type == "RESOURCE_NAME"
    assert vm.values == ["1337"]


def test_values_map_multiple_types() -> None:
    vmdata = '{"type":"TYPES","values":["string",5,5.5,true,false,"5",{"x": 5,"y": 5.5}]}'

    vm = ValuesMap.model_validate_json(vmdata)
    assert vm.type == "TYPES"
    assert vm.values == ["string", 5, 5.5, True, False, "5", Point(x=5, y=5.5)]


def test_values_map_exception_item_not_a_dict() -> None:
    vmdata = """["RESOURCE_NAME", [1211]]"""

    with pytest.raises(ValidationError):
        ValuesMap.model_validate_json(vmdata)


def test_values_map_exception_missing_type() -> None:
    vmdata = """[{"values": [1211]}]"""

    with pytest.raises(ValidationError):
        ValuesMap.model_validate_json(vmdata)


def test_values_map_exception_missing_values() -> None:
    vmdata = """[{"type": "RESOURCE_NAME"}]"""

    with pytest.raises(ValidationError):
        ValuesMap.model_validate_json(vmdata)


def test_values_map_exception_values_not_a_list() -> None:
    vmdata = """[{"type": "RESOURCE_NAME", "values": 1211}]"""

    with pytest.raises(ValidationError):
        ValuesMap.model_validate_json(vmdata)


def test_values_map_exception_unsupported_type() -> None:
    vmdata = """[{"type": "UNSUPPORTED", "values": [{}]}]"""

    with pytest.raises(ValidationError):
        ValuesMap.model_validate_json(vmdata)
