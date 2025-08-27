import graphlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from py_schemax.config import Config
from py_schemax.model import SupportedDataTypes, get_dynamic_dataset_schema
from py_schemax.schema.models import DatasetSchema
from py_schemax.schema.validation import PydanticErrorSchema, ValidationOutputSchema


class Validator(ABC):
    def __init__(self, config: Config):  # pragma: no cover
        self.config = config

    @abstractmethod
    def validate(
        self, *args: Any, **kwargs: Any
    ) -> ValidationOutputSchema:  # pragma: no cover
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
        self.dataset_schema: type[DatasetSchema] = get_dynamic_dataset_schema(config)

    def validate(self, data: dict, file_path: str) -> ValidationOutputSchema:
        try:
            self.dataset_schema.model_validate(data)
        except ValidationError as e:
            return {
                "file_path": file_path,
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
        return {"file_path": file_path, "valid": True, "errors": [], "error_count": 0}

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
                if loc_item not in [dt.name for dt in SupportedDataTypes]:
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
                if loc_length > 1 and (loc_minus_2 := loc[-2]) in [
                    dt.name for dt in SupportedDataTypes
                ]:
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


class UniqueFQNValidator(Validator):
    def __init__(self, config: Config):
        self.config: Config = config
        self.__fqn_to_file_map: dict[str, str] = {}

    def validate(self, data: dict, file_path: str) -> ValidationOutputSchema:
        """Validate the uniqueness of FQNs across multiple validation outputs."""
        current_fqn: str | None = data.get("fqn")

        if current_fqn is None or not isinstance(current_fqn, str):
            return {
                "file_path": file_path,
                "valid": False,
                "errors": [
                    {
                        "type": "missing_fqn",
                        "error_at": "$.fqn",
                        "message": "Duplicate fqn check is enabled but fqn field is missing or invalid",
                        "pydantic_error": None,
                    }
                ],
                "error_count": 1,
            }

        if current_fqn in self.__fqn_to_file_map:
            return {
                "file_path": file_path,
                "valid": False,
                "errors": [
                    {
                        "type": "duplicate_fqn",
                        "error_at": "$.fqn",
                        "message": f"Duplicate FQN '{current_fqn}', already present at '{self.__fqn_to_file_map[current_fqn]}'",
                        "pydantic_error": None,
                    }
                ],
                "error_count": 1,
            }
        self.__fqn_to_file_map[current_fqn] = file_path

        return {"file_path": file_path, "valid": True, "errors": [], "error_count": 0}


class DependencyValidator(Validator):
    def __init__(self, config: Config):
        self.config: Config = config
        self.__sorted_graph: dict[str, list[str]] = {}

    def _validate_field_type(
        self, name: str, value: Any
    ) -> ValidationOutputSchema | None:
        if not isinstance(value, list):
            return {
                "file_path": "",
                "valid": False,
                "errors": [
                    {
                        "type": "invalid_type",
                        "error_at": f"$.{name}",
                        "message": f"'{name}' must be a list",
                        "pydantic_error": None,
                    }
                ],
                "error_count": 1,
            }
        elif not all(isinstance(item, str) for item in value):
            return {
                "file_path": "",
                "valid": False,
                "errors": [
                    {
                        "type": "invalid_type",
                        "error_at": f"$.{name}",
                        "message": f"'{name}' must be a list of strings",
                        "pydantic_error": None,
                    }
                ],
                "error_count": 1,
            }

        return None

    def _add_dependency(self, file_path: str, dependencies: list[str]) -> None:
        self.__sorted_graph[file_path] = dependencies

    def _validate_circular_dependency(self, name: str) -> ValidationOutputSchema | None:
        try:
            graphlib.TopologicalSorter(self.__sorted_graph).prepare()
        except graphlib.CycleError as cycle_error:
            return {
                "file_path": "",
                "valid": False,
                "errors": [
                    {
                        "type": "circular_dependency_detected",
                        "error_at": f"$.{name}",
                        "message": f"circular dependency present: {cycle_error}",
                        "pydantic_error": None,
                    }
                ],
                "error_count": 1,
            }
        return None

    def _validate_for(
        self, field_name: str, data: dict, file_path: str
    ) -> ValidationOutputSchema:
        depends_on = data.get(field_name, [])

        if (error := self._validate_field_type(field_name, depends_on)) is not None:
            return error

        for dep in depends_on:
            if not Path(dep).exists():
                return {
                    "file_path": file_path,
                    "valid": False,
                    "errors": [
                        {
                            "type": "dependent_file_not_found",
                            "error_at": f"$.{field_name}",
                            "message": f"File '{dep}' provided in '{field_name}' field not found",
                            "pydantic_error": None,
                        }
                    ],
                    "error_count": 1,
                }

        self._add_dependency(file_path, depends_on)

        if (error := self._validate_circular_dependency(field_name)) is not None:
            return error

        return {"file_path": file_path, "valid": True, "errors": [], "error_count": 0}

    @abstractmethod
    def validate(
        self, data: dict, file_path: str
    ) -> ValidationOutputSchema:  # pragma: no cover
        """Validate schema dependencies."""
        pass


class DependsOnSchemaValidator(DependencyValidator):
    def __init__(self, config: Config):
        super().__init__(config)

    def validate(self, data: dict, file_path: str) -> ValidationOutputSchema:
        """Validate schema dependencies."""
        return self._validate_for("depends_on", data, file_path)


class DependentsSchemaValidator(DependencyValidator):
    def __init__(self, config: Config):
        super().__init__(config)

    def validate(self, data: dict, file_path: str) -> ValidationOutputSchema:
        return self._validate_for("dependents", data, file_path)
