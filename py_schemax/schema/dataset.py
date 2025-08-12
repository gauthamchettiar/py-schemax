from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Discriminator, Field

# Constants for runtime use
DT_STRING = "string"
DT_INTEGER = "integer"
DT_FLOAT = "float"
DT_BOOLEAN = "boolean"
DT_DATE = "date"
DT_DATETIME = "datetime"

SUPPORTED_DATA_TYPES = [
    DT_STRING,
    DT_INTEGER,
    DT_FLOAT,
    DT_BOOLEAN,
    DT_DATE,
    DT_DATETIME,
]


class BaseDataType(BaseModel):
    model_config = {"extra": "forbid"}  # Reject extra fields

    name: str = Field(
        ..., description="Unique identifier for the column within the dataset"
    )
    unique: bool = Field(
        default=False,
        description="Whether the column values must be unique across all rows in the dataset",
    )
    primary_key: bool = Field(
        default=False,
        description="Whether this column serves as the primary key for the dataset, uniquely identifying each row",
    )
    nullable: bool = Field(
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
        default="YYYY-MM-DD",
        description="Expected date format string using standard date format tokens",
    )


class DateTimeType(BaseDataType):
    type: Literal["datetime"] = Field(
        description="Data type identifier for date and time columns with full timestamp support"
    )
    format: Optional[str] = Field(
        default="YYYY-MM-DD HH:MM:SS",
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

    fqn: str = Field(
        ...,
        description="Fully qualified name of the dataset schema, typically in the format 'namespace.dataset_name'",
    )
    name: str = Field(
        ...,
        description="Name identifying this dataset schema for reference and documentation purposes",
    )
    description: Optional[str] = Field(
        default=None,
        description="Comprehensive description of the dataset's purpose, content, and intended use cases",
    )
    version: str = Field(
        default="1.0",
        description="Schema version following semantic versioning to track schema evolution and compatibility",
    )
    columns: List[DataTypeUnion] = Field(
        ...,
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
