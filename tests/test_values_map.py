import json

import pytest

from toadr3 import SchemaError, parse_values_map


def test_values_map():
    vm = json.loads(
        """
        [
            {"type": "RESOURCE_NAME", "values": [1211]},
            {"type": "ORGANIZATION_ID", "values": ["1337"]},
            {
                "type": "TYPES",
                "values": ["string", 5, 5.5, true, false, "5", {"x": 5, "y": 5.5}]
            }
        ]
        """
    )

    res = parse_values_map(vm)

    assert "RESOURCE_NAME" in res
    assert res["RESOURCE_NAME"] == [1211]
    assert "ORGANIZATION_ID" in res
    assert res["ORGANIZATION_ID"] == ["1337"]
    assert "TYPES" in res
    assert res["TYPES"] == ["string", 5, 5.5, True, False, "5", (5, 5.5)]


def test_values_map_exception_not_a_list():
    vm = json.loads(
        """
        {
            "type": "RESOURCE_NAME", "values": [1211]
        }
        """
    )

    with pytest.raises(SchemaError) as e:
        parse_values_map(vm)

    assert str(e.value) == "Expected 'valuesMap' to be an array."


def test_values_map_exception_item_not_a_dict():
    vm = json.loads("""[["RESOURCE_NAME", [1211]]]""")

    with pytest.raises(SchemaError) as e:
        parse_values_map(vm)

    assert str(e.value) == "Expected 'valuesMap' to contain objects."


def test_values_map_exception_missing_type():
    vm = json.loads("""[{"values": [1211]}]""")

    with pytest.raises(SchemaError) as e:
        parse_values_map(vm)

    assert str(e.value) == "Missing 'type' in values map schema."


def test_values_map_exception_missing_values():
    vm = json.loads("""[{"type": "RESOURCE_NAME"}]""")

    with pytest.raises(SchemaError) as e:
        parse_values_map(vm)

    assert str(e.value) == "Missing 'values' in values map schema for 'RESOURCE_NAME'."


def test_values_map_exception_values_not_a_list():
    vm = json.loads("""[{"type": "RESOURCE_NAME", "values": 1211}]""")

    with pytest.raises(SchemaError) as e:
        parse_values_map(vm)

    assert str(e.value) == "Expected 'values' for 'RESOURCE_NAME' to be an array."


def test_values_map_exception_unsupported_type():
    vm = json.loads("""[{"type": "UNSUPPORTED", "values": [{}]}]""")

    with pytest.raises(SchemaError) as e:
        parse_values_map(vm)

    assert str(e.value) == "Unsupported type for 'UNSUPPORTED': '{}' in values map schema"


def test_values_map_exception_duplicate_value():
    vm = json.loads(
        """
        [
            {"type": "RESOURCE_NAME", "values": [1211]},
            {"type": "RESOURCE_NAME", "values": [1212]}
        ]
        """
    )

    with pytest.raises(SchemaError) as e:
        parse_values_map(vm)

    assert str(e.value) == "Duplicate type 'RESOURCE_NAME' in values map schema."
