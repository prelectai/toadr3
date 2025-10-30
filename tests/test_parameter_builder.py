from typing import Any

import pytest

from toadr3._internal import (
    ClientName,
    EventID,
    Objects,
    ParameterBuilder,
    ProgramID,
    QueryParams,
    SkipAndLimit,
    SubscriptionID,
    Targets,
)
from toadr3._internal.object_id import ObjectID
from toadr3.models import ObjectType, TargetType


def test_client_name() -> None:
    args = {"client_name": "YAC"}

    errors: list[str] = []
    ClientName.check_query_parameters(errors, args)
    assert len(errors) == 0

    params: QueryParams = {}
    ClientName.create_query_parameters(params, args)

    assert len(params) == 1
    assert params["clientName"] == "YAC"


@pytest.mark.parametrize("object_id_class", [EventID, ProgramID, SubscriptionID])
def test_object_id(object_id_class: type[ObjectID]) -> None:
    arg_name = object_id_class._attribute[0]  # noqa: SLF001
    param_name = object_id_class._attribute[1]  # noqa: SLF001
    args = {
        arg_name: "Valid-ID_5",
    }

    errors: list[str] = []
    object_id_class.check_query_parameters(errors, args)
    assert len(errors) == 0

    params: QueryParams = {}
    object_id_class.create_query_parameters(params, args)
    assert len(params) == 1
    assert params[param_name] == "Valid-ID_5"


@pytest.mark.parametrize("object_id_class", [EventID, ProgramID, SubscriptionID])
def test_object_id_error_empty_string(object_id_class: type[ObjectID]) -> None:
    arg_name = object_id_class._attribute[0]  # noqa: SLF001
    args = {
        arg_name: "",
    }

    errors: list[str] = []
    object_id_class.check_query_parameters(errors, args)
    assert len(errors) == 1
    assert errors[0] == f"{arg_name} must be between 1 and 128 characters long"


@pytest.mark.parametrize("object_id_class", [EventID, ProgramID, SubscriptionID])
def test_object_id_error_invalid_id(object_id_class: type[ObjectID]) -> None:
    arg_name = object_id_class._attribute[0]  # noqa: SLF001
    args = {
        arg_name: "Invalid@ID++",
    }

    errors: list[str] = []
    object_id_class.check_query_parameters(errors, args)
    assert len(errors) == 1
    assert errors[0] == f"{arg_name} '{args[arg_name]}' does not match regex '^[a-zA-Z0-9_-]*$'"


@pytest.mark.parametrize("object_id_class", [EventID, ProgramID, SubscriptionID])
def test_object_id_error_int(object_id_class: type[ObjectID]) -> None:
    arg_name = object_id_class._attribute[0]  # noqa: SLF001
    args = {
        arg_name: 1,
    }

    errors: list[str] = []
    object_id_class.check_query_parameters(errors, args)
    assert len(errors) == 1
    assert errors[0] == f"{arg_name} must be a string"


@pytest.mark.parametrize("object_id_class", [EventID, ProgramID, SubscriptionID])
def test_object_id_error_none(object_id_class: type[ObjectID]) -> None:
    arg_name = object_id_class._attribute[0]  # noqa: SLF001
    args = {
        arg_name: None,
    }

    errors: list[str] = []
    object_id_class.check_query_parameters(errors, args)
    if object_id_class._nullable:  # noqa: SLF001
        assert len(errors) == 0
    else:
        assert len(errors) == 1
        assert errors[0] == f"{arg_name} cannot be None"


def test_skip_and_limit() -> None:
    args = {"skip": 5, "limit": 10}
    errors: list[str] = []
    SkipAndLimit.check_query_parameters(errors, args)
    assert len(errors) == 0

    params: QueryParams = {}
    SkipAndLimit.create_query_parameters(params, args)
    assert len(params) == 2
    assert params["skip"] == 5
    assert params["limit"] == 10


def test_skip_and_limit_errors() -> None:
    args: dict[str, Any] = {"skip": "5", "limit": "10"}
    errors: list[str] = []
    SkipAndLimit.check_query_parameters(errors, args)
    assert len(errors) == 2
    assert errors[0] == "skip must be an integer"
    assert errors[1] == "limit must be an integer"

    args = {"skip": -1, "limit": -1}
    errors.clear()
    SkipAndLimit.check_query_parameters(errors, args)
    assert len(errors) == 2
    assert errors[0] == "skip must be a positive integer"
    assert errors[1] == "limit must be a positive integer"


def test_objects() -> None:
    args = {"objects": [ObjectType.EVENT, "PROGRAM"]}
    errors: list[str] = []
    Objects.check_query_parameters(errors, args)
    assert len(errors) == 0

    params: QueryParams = {}
    Objects.create_query_parameters(params, args)
    assert len(params) == 1
    assert params["objects"] == ["EVENT", "PROGRAM"]


def test_objects_errors() -> None:
    args: dict[str, Any] = {"objects": "EVENT"}
    errors: list[str] = []
    Objects.check_query_parameters(errors, args)
    assert len(errors) == 1
    assert errors[0] == "objects must be a list of strings or ObjectType"

    args = {"objects": [1, 2]}
    errors.clear()
    Objects.check_query_parameters(errors, args)
    assert len(errors) == 2

    assert errors[0] == "object type '1' must be of type string or ObjectType"
    assert errors[1] == "object type '2' must be of type string or ObjectType"

    args = {"objects": ["EVNENT", "SUPSCRIBTION"]}
    errors.clear()
    Objects.check_query_parameters(errors, args)
    assert len(errors) == 2

    all_types = ", ".join([f"'{item}'" for item in ObjectType])
    assert errors[0] == f"object type 'EVNENT' must be one of [{all_types}]"
    assert errors[1] == f"object type 'SUPSCRIBTION' must be one of [{all_types}]"


def test_targets() -> None:
    args: dict[str, Any] = {"target_type": TargetType.VEN_NAME, "target_values": ["121"]}
    errors: list[str] = []
    Targets.check_query_parameters(errors, args)
    assert len(errors) == 0

    params: QueryParams = {}
    Targets.create_query_parameters(params, args)
    assert len(params) == 2
    assert params["targetType"] == "VEN_NAME"
    assert params["targetValues"] == ["121"]


def test_targets_errors() -> None:
    args: dict[str, Any] = {"target_type": TargetType.VEN_NAME}
    errors: list[str] = []
    Targets.check_query_parameters(errors, args)
    assert len(errors) == 1
    assert errors[0] == "target_values are required when target_type is provided"

    args = {"target_values": ["121"]}
    errors.clear()
    Targets.check_query_parameters(errors, args)
    assert len(errors) == 1
    assert errors[0] == "target_type is required when target_values are provided"

    args = {"target_type": "VEN_NAME", "target_values": "121"}
    errors.clear()
    Targets.check_query_parameters(errors, args)
    assert len(errors) == 1
    assert errors[0] == "target_values must be a list of strings"

    args = {"target_type": 121, "target_values": ["121"]}
    errors.clear()
    Targets.check_query_parameters(errors, args)
    assert len(errors) == 1
    assert errors[0] == "target_type must be TargetType or str"


def test_empty_parameter_builder() -> None:
    pb = ParameterBuilder()

    pb.check_query_parameters({})
    res = pb.build_query_parameters({}, {})
    assert res == {}


def test_parameter_builder() -> None:
    pb = ParameterBuilder(SkipAndLimit)

    pb.check_query_parameters({})
    params = pb.build_query_parameters({}, {})
    assert params == {}

    params = pb.build_query_parameters({"skip": 1}, {})
    assert params == {"skip": 1}

    params = pb.build_query_parameters({}, {"skip": 2})
    assert params == {"skip": 2}

    # custom params does not override args
    params = pb.build_query_parameters({"skip": 1}, {"skip": 2})
    assert params == {"skip": 1}


def test_parameter_builder_errors() -> None:
    pb = ParameterBuilder(SkipAndLimit)
    with pytest.raises(ValueError, match="skip must be a positive integer"):
        pb.check_query_parameters({"skip": -1})
