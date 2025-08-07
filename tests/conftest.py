"""Pytest configuration and fixtures for py-schemax tests."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path("tests") / "fixtures"


@pytest.fixture
def valid_schemas_dir(fixtures_dir) -> Path:
    """Return the path to the valid schemas fixtures directory."""
    return fixtures_dir / "valid_schemas"


@pytest.fixture
def invalid_schemas_dir(fixtures_dir) -> Path:
    """Return the path to the invalid schemas fixtures directory."""
    return fixtures_dir / "invalid_schemas"


@pytest.fixture
def valid_schemas(valid_schemas_dir) -> dict[str, Path]:
    """Return the path to a simple valid YAML schema file."""
    return {
        "valid_simple_schema": valid_schemas_dir / "valid_simple_schema.json",
        "valid_complex_schema": valid_schemas_dir / "valid_complex_schema.yaml",
    }


@pytest.fixture
def invalid_schemas(invalid_schemas_dir) -> dict[str, Path]:
    """Return the path to a complex YAML schema file."""
    return {
        "invalid_columns": invalid_schemas_dir / "invalid_columns.yaml",
        "invalid_json": invalid_schemas_dir / "invalid_json.json",
        "invalid_missing_columns": invalid_schemas_dir / "invalid_missing_columns.yaml",
        "invalid_missing_name": invalid_schemas_dir / "invalid_missing_name.json",
        "invalid_types": invalid_schemas_dir / "invalid_types.json",
        "invalid_unsupported_format": invalid_schemas_dir
        / "invalid_unsupported_format.txt",
        "invalid_yaml": invalid_schemas_dir / "invalid_yaml.yaml",
    }


@pytest.fixture
def dataset_with_reqd_fields():
    """Return a dictionary of required fields for Pydantic models."""
    return {
        "fqn": "namespace.dataset_name",
        "name": "Dataset Name",
        "version": "1.0",
        "columns": [],
    }


@pytest.fixture
def dataset_with_optional_fields(dataset_with_reqd_fields):
    """Return a dictionary of required and optional fields for Pydantic models."""
    return dataset_with_reqd_fields | {
        "description": "This is a test dataset schema",
        "tags": ["test", "example"],
        "metadata": {"source": "Generated for testing", "frequency": "daily"},
        "inherits": [],
        "inherited_by": [],
    }


@pytest.fixture
def dataset_with_columns(dataset_with_optional_fields):
    """Return a dictionary with valid columns added to the dataset."""
    return dataset_with_optional_fields | {
        "columns": [
            {
                "name": "column1",
                "type": "string",
                "max_length": 255,
                "min_length": 1,
                "pattern": "^[a-zA-Z0-9_]+$",
            },
            {"name": "column2", "type": "integer", "minimum": 0, "maximum": 100},
            {
                "name": "column3",
                "type": "float",
                "minimum": 0.0,
                "maximum": 100.0,
                "precision": 2,
            },
            {"name": "column4", "type": "boolean"},
            {"name": "column5", "type": "date", "format": "YYYY-MM-DD"},
            {
                "name": "column6",
                "type": "datetime",
                "format": "YYYY-MM-DDTHH:mm:ssZ",
                "timezone": "UTC",
            },
        ]
    }
