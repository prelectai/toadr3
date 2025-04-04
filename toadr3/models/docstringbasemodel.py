from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class DocstringBaseModel(BaseModel):
    """BaseModel that supports docstrings for field descriptions."""

    model_config = ConfigDict(
        use_attribute_docstrings=True,
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel,
        ),
        serialize_by_alias=True,
        validate_by_alias=True,
        validate_by_name=True,
    )

    def __str__(self) -> str:
        """Return a string representation of the object."""
        return f"{self.__class__.__name__}({super().__str__()})"
