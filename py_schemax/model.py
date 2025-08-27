import typing
from enum import Enum
from typing import Annotated, Dict, List, Optional, Type, Union, Unpack

from pydantic import Discriminator, Field, create_model

from py_schemax.config import Config
from py_schemax.schema.models import (
    BaseDataType,
    BooleanType,
    DatasetSchema,
    DateTimeType,
    DateType,
    FloatType,
    IntegerType,
    StringType,
)


class SupportedDataTypes(Enum):
    string = StringType
    integer = IntegerType
    float = FloatType
    boolean = BooleanType
    date = DateType
    datetime = DateTimeType


@typing.no_type_check
def __create_dynamic_data_type(
    base_model: Type[BaseDataType], type_name: str, required_fields: List[str]
) -> Type[BaseDataType]:
    """Create a dynamic data type model with specified required fields."""
    fields = {}
    required_fields_set = set(required_fields or [])

    for field_name, model_field in base_model.model_fields.items():
        if field_name in required_fields_set:
            # Make field required by removing default and setting ... (Ellipsis)
            fields[field_name] = (
                model_field.annotation,
                Field(..., description=model_field.description),
            )
        else:
            # Keep original field definition
            fields[field_name] = (model_field.annotation, model_field)

    return create_model(
        f"Dynamic{type_name}",
        __config__=base_model.model_config,
        __base__=base_model,
        **fields,
    )


def get_dynamic_data_types(config: Config) -> Dict[str, type[BaseDataType]]:
    """Create dynamic data type models based on configuration."""
    column_required_attributes = config.column_required_attributes or {}

    dynamic_types = {}

    for data_type in SupportedDataTypes:
        base_model = data_type.value
        required_fields = column_required_attributes.get(data_type.name, [])
        dynamic_types[data_type.name] = __create_dynamic_data_type(
            base_model, base_model.__name__, required_fields
        )

    return dynamic_types


@typing.no_type_check
def get_dynamic_dataset_schema(config: Config) -> type[DatasetSchema]:
    dynamic_data_types = get_dynamic_data_types(config)

    DynamicDataTypeUnion = Annotated[  # type: ignore [valid-type]
        Union[tuple(dynamic_data_types.values())],
        Discriminator("type"),
    ]

    fields = {}
    required_fields = set(config.model_required_attributes or [])

    for field_name, model_field in DatasetSchema.model_fields.items():
        if field_name == "columns":
            # Handle columns field specially to use dynamic types
            if field_name in required_fields:
                fields[field_name] = (
                    List[DynamicDataTypeUnion],  # type: ignore [valid-type]
                    Field(..., description=model_field.description),
                )
            else:
                fields[field_name] = (
                    Optional[List[DynamicDataTypeUnion]],  # type: ignore [valid-type]
                    Field(default=None, description=model_field.description),
                )
        else:
            # Handle other fields normally
            if field_name in required_fields:
                fields[field_name] = (
                    model_field.annotation,
                    Field(..., description=model_field.description),
                )
            else:
                fields[field_name] = (model_field.annotation, model_field)

    return create_model(
        "DynamicDatasetSchema",
        __config__=DatasetSchema.model_config,
        __base__=DatasetSchema,
        **fields,
    )
