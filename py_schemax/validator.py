import json
from pathlib import Path

import yaml
from cachebox import LRUCache
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from .cache import persistent_cachedmethod
from .schema.dataset import DatasetSchema
from .schema.validation import PydanticErrorSchema, ValidationOutputSchema


@persistent_cachedmethod(".schemax/validation.pickle", LRUCache(maxsize=10000))
def validate_schema_file(
    path: str | Path, file_hash: str | None
) -> ValidationOutputSchema:
    """Validate a file against the DatasetSchema and return structured JSON result.

    Args:
        path: Path to the file to validate
    Returns:
        Dictionary with validation results suitable for JSON output
    """
    path_str = str(path)
    path = Path(path) if isinstance(path, str) else path
    if not path.exists():
        return {
            "file_path": path_str,
            "valid": False,
            "errors": [
                {
                    "type": "file_not_found",
                    "error_at": "$",
                    "message": f"'{path_str}' not found",
                    "pydantic_error": None,
                }
            ],
            "error_count": 1,
        }

    try:
        if path.suffix.lower() == ".json":
            with open(path, "r") as f:
                data = json.load(f)
        elif path.suffix.lower() in [".yml", ".yaml"]:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        else:
            return {
                "file_path": path_str,
                "valid": False,
                "errors": [
                    {
                        "type": "unsupported_format",
                        "error_at": "$",
                        "message": f"'{path_str}' of type '{path.suffix}' not supported",
                        "pydantic_error": None,
                    }
                ],
                "error_count": 1,
            }
    except (json.JSONDecodeError, yaml.YAMLError) as _:
        return {
            "file_path": path_str,
            "valid": False,
            "errors": [
                {
                    "type": "parse_error",
                    "error_at": "$",
                    "message": "error parsing file",
                    "pydantic_error": None,
                }
            ],
            "error_count": 1,
        }

    return validate_schema(data, file_path=path_str)


def validate_schema(data: dict, file_path: str | None = None) -> ValidationOutputSchema:
    """Validate a dictionary against the DatasetSchema and return structured JSON result.

    Args:
        data: Dictionary to validate
    Returns:
        Dictionary with validation results suitable for JSON output
    """
    file_path = file_path or "in-memory"

    try:
        DatasetSchema(**data)
    except ValidationError as e:
        return {
            "file_path": file_path,
            "valid": False,
            "errors": [
                {
                    "type": "validation_error",
                    "error_at": _format_loc_as_jsonql(error),
                    "message": _format_pydantic_error_as_text(error),
                    "pydantic_error": _strip_details(error),
                }
                for error in e.errors()
            ],
            "error_count": len(e.errors()),
        }
    return {"file_path": file_path, "valid": True, "errors": [], "error_count": 0}


def _strip_details(error: ErrorDetails) -> PydanticErrorSchema:
    """Strip details from the error for JSON serialization."""
    return {
        "type": error["type"],
        "msg": error["msg"],
    }


def _format_loc_as_jsonql(error: ErrorDetails) -> str:
    """Format location for JSONPath-like output."""
    error_string = "$"
    for loc_item in error["loc"]:
        if isinstance(loc_item, int):
            error_string += f"[{loc_item}]"
        elif isinstance(loc_item, str):
            if loc_item not in [
                "string",
                "integer",
                "float",
                "boolean",
                "date",
                "datetime",
                "array",
                "dict",
            ]:
                error_string += f".{loc_item}"
    return error_string


def _format_pydantic_error_as_text(error: ErrorDetails) -> str:
    """Format error for output."""
    match error["type"]:
        case "extra_forbidden":
            loc_minus_1 = error["loc"][-1]
            loc_minus_2 = error["loc"][-2]
            error_string = f"'{loc_minus_1}' invalid attribute for '{loc_minus_2}' type"
        case "missing":
            loc_minus_1 = error["loc"][-1]
            error_string = f"'{loc_minus_1}' attribute missing"
        case "int_parsing" | "float_parsing" | "str_parsing" | "bool_parsing":
            loc_minus_2 = error["loc"][-2]
            error_string = f"expected to be '{loc_minus_2}'"
        case "model_attributes_type":
            error_string = "expected to be an 'object'"
        case "union_tag_invalid":
            expected_tags = error.get("ctx", {}).get("expected_tags", [])
            error_string = f"'type' expected to be one of {expected_tags}"
        case "union_tag_not_found":
            error_string = "'type' attribute missing"
        case _:
            msg = error["msg"]
            error_string = f"{msg}"

    return error_string
