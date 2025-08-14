import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from py_schemax.cache import Cache
from py_schemax.config import Config
from py_schemax.schema.dataset import SUPPORTED_DATA_TYPES, DatasetSchema
from py_schemax.schema.validation import PydanticErrorSchema, ValidationOutputSchema
from py_schemax.utils import get_hash_of_file, merge_validation_outputs


class Validator(ABC):
    def __init__(self, config: Config):  # pragma: no cover
        self.config = config

    @abstractmethod
    def validate(
        self, *args: Any, **kwargs: Any
    ) -> ValidationOutputSchema:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def validated_content(self) -> Any:  # pragma: no cover
        pass


class FileValidator(Validator):
    def __init__(self, config: Config):
        self.config: Config = config
        self.__validated_content: dict | None = None

    def validate(self, file_path: str | Path) -> ValidationOutputSchema:
        path_str = str(file_path)
        path = Path(file_path) if isinstance(file_path, str) else file_path
        if not path.exists():
            return {
                "file_path": path_str,
                "valid": False,
                "errors": [
                    {
                        "type": "file_not_found",
                        "error_at": "$",
                        "message": f"'{file_path}' not found",
                        "pydantic_error": None,
                    }
                ],
                "error_count": 1,
            }
        try:
            if path.suffix.lower() == ".json":
                with open(path, "r") as f:
                    self.__validated_content = json.load(f)
            elif path.suffix.lower() in [".yml", ".yaml"]:
                with open(path, "r") as f:
                    self.__validated_content = yaml.safe_load(f)
            else:
                return {
                    "file_path": path_str,
                    "valid": False,
                    "errors": [
                        {
                            "type": "unsupported_format",
                            "error_at": "$",
                            "message": f"'{file_path}' of type '{path.suffix}' not supported",
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
        return {
            "file_path": path_str,
            "valid": True,
            "errors": [],
            "error_count": 0,
        }

    @property
    def validated_content(self) -> dict | None:
        """Return the validated content of the file."""
        return self.__validated_content


class PydanticSchemaValidator(Validator):
    def __init__(self, config: Config):
        self.config: Config = config
        self.__validated_content: DatasetSchema | None = None

    def validate(self, data: dict) -> ValidationOutputSchema:
        try:
            self.__validated_content = DatasetSchema.model_validate(data)
        except ValidationError as e:
            return {
                "file_path": "",
                "valid": False,
                "errors": [
                    {
                        "type": "validation_error",
                        "error_at": self.__format_loc_as_jsonql(error),
                        "message": self.__format_pydantic_error_as_text(error),
                        "pydantic_error": self.__strip_details(error),
                    }
                    for error in e.errors()
                ],
                "error_count": len(e.errors()),
            }
        return {"file_path": "", "valid": True, "errors": [], "error_count": 0}

    def __strip_details(self, error: ErrorDetails) -> PydanticErrorSchema:
        """Strip details from the error for JSON serialization."""
        return {
            "type": error["type"],
            "msg": error["msg"],
        }

    def __format_loc_as_jsonql(self, error: ErrorDetails) -> str:
        """Format location for JSONPath-like output."""
        error_string = "$"
        for loc_item in error["loc"]:
            if isinstance(loc_item, int):
                error_string += f"[{loc_item}]"
            elif isinstance(loc_item, str):
                if loc_item not in SUPPORTED_DATA_TYPES:
                    error_string += f".{loc_item}"
        if error["type"] == "union_tag_invalid":
            discriminator = error.get("ctx", {}).get("discriminator", "").strip("'")
            error_string += f".{discriminator}"
        return error_string

    def __format_pydantic_error_as_text(self, error: ErrorDetails) -> str:
        """Format error for output."""
        error_string, loc = error["msg"], error["loc"] or ["$"]
        loc_length = len(loc)
        match error["type"]:
            case "extra_forbidden":
                if loc_length > 1 and (loc_minus_2 := loc[-2]) in SUPPORTED_DATA_TYPES:
                    error_string = (
                        f"'{loc[-1]}' invalid attribute for '{loc_minus_2}' type"
                    )
                elif loc_length == 1:
                    error_string = f"invalid attribute '{loc[0]}' provided"
            case "missing":
                if loc_length > 0:
                    error_string = f"'{loc[-1]}' attribute missing"
            case "int_parsing" | "int_from_float" | "float_parsing" | "bool_parsing":
                if loc_length > 0:
                    exp_type = error["type"].split("_")[0]
                    error_string = f"'{loc[-1]}' expected to be '{exp_type}' type"
            case "int_type" | "float_type" | "string_type" | "list_type" | "model_type":
                if loc_length > 0:
                    exp_type = error["type"].split("_")[0]
                    exp_type = "object" if exp_type == "model" else exp_type
                    error_string = f"'{loc[-1]}' expected to be '{exp_type}' type"
            case "union_tag_invalid":
                expected_tags = error.get("ctx", {}).get("expected_tags", [])
                discriminator = error.get("ctx", {}).get("discriminator", "").strip("'")
                if expected_tags:
                    error_string = (
                        f"'{discriminator}' expected to be one of [{expected_tags}]"
                    )
            case "union_tag_not_found":
                error_string = "'type' attribute missing"

        return error_string

    @property
    def validated_content(self) -> DatasetSchema | None:
        """Return the validated content of the file."""
        return self.__validated_content


def validate_file(config: Config, file_path: str | Path) -> ValidationOutputSchema:
    """Validate a file using the appropriate validator based on its extension."""

    file_validator = FileValidator(config)
    if (file_validator_output := file_validator.validate(file_path))["valid"] is False:
        return file_validator_output
    else:
        pydantic_validator = PydanticSchemaValidator(config)
        if (
            pydantic_validator_output := pydantic_validator.validate(
                file_validator.validated_content or {}
            )
        )["valid"] is False:
            return merge_validation_outputs(
                file_validator_output, pydantic_validator_output
            )

    return file_validator_output


def get_validation_output_from_cache(
    config: Config, cache: Cache, file_path: str | Path
) -> ValidationOutputSchema | None:
    try:
        file_hash = get_hash_of_file(str(file_path))
    except FileNotFoundError:
        file_hash = None

    return cache.read(file_path, file_hash)  # type: ignore


def get_validation_output_from_cache_or_validate(
    config: Config, cache: Cache, file_path: str | Path
) -> ValidationOutputSchema:
    if (
        cached_result := get_validation_output_from_cache(config, cache, file_path)
    ) is not None:
        return cached_result

    return validate_file(config, file_path)
