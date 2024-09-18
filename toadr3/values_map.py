from typing import Any

from .exceptions import SchemaError


def parse_values_map(data: list) -> dict[str, Any]:
    """Parse a values map object into a dictionary.

    The values map object is a list of objects, each with a 'type' and 'values' key.
    Technically, the 'key' can be duplicated, but we assume that it is unique. If we find
    documentation that says otherwise, we can change this. But it would be nice to know if
    the values of duplicate keys can be combined or if they must be handled separately before
    we make that change.

    Parameters
    ----------
    data : list
        The values map object from a JSON.

    Returns
    -------
    dict
        The parsed values map object as a dictionary.
    """
    if not isinstance(data, list):
        raise SchemaError("Expected 'valuesMap' to be an array.")

    result = {}
    for item in data:
        if not isinstance(item, dict):
            raise SchemaError("Expected 'valuesMap' to contain objects.")

        if "type" not in item:
            raise SchemaError("Missing 'type' in values map schema.")

        if "values" not in item:
            raise SchemaError(f"Missing 'values' in values map schema for '{item['type']}'.")

        if not isinstance(item["values"], list):
            raise SchemaError(f"Expected 'values' for '{item['type']}' to be an array.")

        if item["type"] in result:
            raise SchemaError(f"Duplicate type '{item['type']}' in values map schema.")

        result[item["type"]] = []
        for value in item["values"]:
            match value:
                case bool() | float() | int() | str():
                    result[item["type"]].append(value)
                case {"x": x, "y": y}:  # Point
                    # we currently store this as a tuple
                    result[item["type"]].append((x, y))
                case _:
                    msg = f"Unsupported type for '{item['type']}': '{value}' in values map schema"
                    raise SchemaError(msg)
    return result
