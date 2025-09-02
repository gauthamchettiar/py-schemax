import typing
from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Type, Union

from pydantic import BaseModel, Discriminator, Field, create_model

from py_schemax.config import Config


class BaseDataType(BaseModel):
    model_config = {"extra": "forbid"}  # Reject extra fields

    name: Optional[str] = Field(
        default=None, description="Unique identifier for the column within the dataset"
    )
    unique: Optional[bool] = Field(
        default=False,
        description="Whether the column values must be unique across all rows in the dataset",
    )
    primary_key: Optional[bool] = Field(
        default=False,
        description="Whether this column serves as the primary key for the dataset, uniquely identifying each row",
    )
    nullable: Optional[bool] = Field(
        default=True,
        description="Whether the column can contain null/None values. Set to False for required fields",
    )
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description explaining the purpose and content of this column",
    )


class StringType(BaseDataType):
    type: Literal["string"] = Field(
        description="Data type identifier for text/string columns"
    )
    max_length: Optional[int] = Field(
        default=None,
        description="Maximum allowed number of characters in the string value",
    )
    min_length: Optional[int] = Field(
        default=None,
        description="Minimum required number of characters in the string value",
    )
    pattern: Optional[str] = Field(
        default=None,
        description="Regular expression pattern that string values must match for validation",
    )


class IntegerType(BaseDataType):
    type: Literal["integer"] = Field(
        description="Data type identifier for whole number columns"
    )
    minimum: Optional[int] = Field(
        default=None, description="Minimum allowed integer value (inclusive)"
    )
    maximum: Optional[int] = Field(
        default=None, description="Maximum allowed integer value (inclusive)"
    )


class FloatType(BaseDataType):
    type: Literal["float"] = Field(
        description="Data type identifier for decimal number columns"
    )
    minimum: Optional[float] = Field(
        default=None, description="Minimum allowed floating-point value (inclusive)"
    )
    maximum: Optional[float] = Field(
        default=None, description="Maximum allowed floating-point value (inclusive)"
    )
    precision: Optional[int] = Field(
        default=None,
        description="Number of decimal places to maintain for floating-point values",
    )


class BooleanType(BaseDataType):
    type: Literal["boolean"] = Field(
        description="Data type identifier for true/false columns"
    )


class DateType(BaseDataType):
    type: Literal["date"] = Field(
        description="Data type identifier for date-only columns (no time component)"
    )
    format: Optional[str] = Field(
        default=None,
        description="Expected date format string using standard date format tokens",
    )


class DateTimeType(BaseDataType):
    type: Literal["datetime"] = Field(
        description="Data type identifier for date and time columns with full timestamp support"
    )
    format: Optional[str] = Field(
        default=None,
        description="Expected datetime format string using standard datetime format tokens",
    )
    timezone: Optional[str] = Field(
        default=None,
        description="Timezone identifier (e.g., 'UTC', 'America/New_York') for datetime interpretation",
    )


DataTypeUnion = Annotated[
    Union[StringType, IntegerType, FloatType, BooleanType, DateType, DateTimeType],
    Discriminator("type"),
]


class DatasetSchema(BaseModel):
    model_config = {"extra": "forbid"}  # Reject extra fields

    fqn: Optional[str] = Field(
        default=None,
        description="Fully qualified name of the dataset schema, typically in the format 'namespace.dataset_name'",
    )
    name: Optional[str] = Field(
        default=None,
        description="Name identifying this dataset schema for reference and documentation purposes",
    )
    description: Optional[str] = Field(
        default=None,
        description="Comprehensive description of the dataset's purpose, content, and intended use cases",
    )
    version: Optional[str] = Field(
        default=None,
        description="Schema version following semantic versioning to track schema evolution and compatibility",
    )
    columns: Optional[List[DataTypeUnion]] = Field(
        default=None,
        description="Complete list of column definitions that make up the dataset structure, each with its own validation rules",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional schema-level information such as data source, update frequency, or custom attributes",
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="List of tags or keywords associated with the dataset for easier categorization and searchability",
    )
    depends_on: Optional[List[str]] = Field(
        default=None,
        description="List of file paths that this dataset depends on",
    )
    dependents: Optional[List[str]] = Field(
        default=None,
        description="List of file paths that depend on this dataset",
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
