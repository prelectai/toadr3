from typing import Any

from toadr3.models import ObjectType

from .query_parameter import QueryParameter, QueryParams

_OBJECT_TYPES = [str(item) for item in ObjectType]


class Objects(QueryParameter):
    """Objects query parameter.

    objects: list[str] | list[ObjectType] | None
        The object types to filter the items by.
    """

    @staticmethod
    def create_query_parameters(params: QueryParams, args: dict[str, Any]) -> None:
        """Add objects parameter."""
        objects = args.get("objects")
        if objects is not None:
            object_names: list[str] = []
            for obj_name in objects:
                if isinstance(obj_name, ObjectType):
                    object_names.append(obj_name.value)
                else:
                    object_names.append(obj_name)
            params["objects"] = object_names

    @staticmethod
    def check_query_parameters(errors: list[str], args: dict[str, Any]) -> None:
        """Check if objects parameter is valid."""
        objects = args.get("objects")
        if objects is not None:
            if not isinstance(objects, list):
                errors.append("objects must be a list of strings or ObjectType")
            else:
                for item in objects:
                    if not isinstance(item, (ObjectType, str)):
                        errors.append(f"object type '{item}' must be of type string or ObjectType")
                    elif str(item) not in _OBJECT_TYPES:
                        errors.append(f"object type '{item}' must be one of {_OBJECT_TYPES}")
