from typing import List, Optional, TypedDict


class PydanticErrorSchema(TypedDict):
    """Schema for Pydantic error details."""

    type: str
    msg: str


class ValidationErrorSchema(TypedDict):
    """Schema for error details."""

    type: str
    error_at: str
    message: str
    pydantic_error: Optional[PydanticErrorSchema]


class ValidationOutputSchema(TypedDict):
    """Schema for the output of the validate function."""

    file_path: str
    valid: bool
    error_count: int
    errors: List[ValidationErrorSchema]
