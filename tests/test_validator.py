import pytest

from py_schemax.schema.dataset import SUPPORTED_DATA_TYPES
from py_schemax.validator import validate_schema, validate_schema_file


class TestNonPydanticErrors:
    def test_file_not_found(self, invalid_schemas):
        result = validate_schema_file(
            invalid_schemas["invalid_missing_file"], None, cachebox__ignore=True
        )
        assert result == {
            "file_path": str(invalid_schemas["invalid_missing_file"]),
            "valid": False,
            "errors": [
                {
                    "type": "file_not_found",
                    "error_at": "$",
                    "message": f"'{invalid_schemas['invalid_missing_file']}' not found",
                    "pydantic_error": None,
                }
            ],
            "error_count": 1,
        }

    def test_unsupported_format(self, invalid_schemas):
        result = validate_schema_file(
            invalid_schemas["invalid_unsupported_format"], None, cachebox__ignore=True
        )
        assert result == {
            "file_path": str(invalid_schemas["invalid_unsupported_format"]),
            "valid": False,
            "errors": [
                {
                    "type": "unsupported_format",
                    "error_at": "$",
                    "message": f"'{invalid_schemas['invalid_unsupported_format']}' of type '.txt' not supported",
                    "pydantic_error": None,
                }
            ],
            "error_count": 1,
        }

    def test_invalid_json(self, invalid_schemas):
        result = validate_schema_file(
            invalid_schemas["invalid_json"], None, cachebox__ignore=True
        )
        assert result == {
            "file_path": str(invalid_schemas["invalid_json"]),
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

    def test_invalid_yaml(self, invalid_schemas):
        result = validate_schema_file(
            invalid_schemas["invalid_yaml"], None, cachebox__ignore=True
        )
        assert result == {
            "file_path": str(invalid_schemas["invalid_yaml"]),
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


class TestPydanticValidationErrors:
    def test_extra_fields_at_root(self):
        inp = {
            "name": "Test Dataset",
            "fqn": "com.example.TestDataset",
            "description": "This dataset has extra fields not defined in the schema.",
            "columns": [],
            "extra_field": "This should not be here",
            "extra_field2": "This should not be here either",
        }
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 2
        assert result["errors"][0]["error_at"] == "$.extra_field"
        assert (
            result["errors"][0]["message"] == "invalid attribute 'extra_field' provided"
        )
        assert result["errors"][1]["error_at"] == "$.extra_field2"
        assert (
            result["errors"][1]["message"]
            == "invalid attribute 'extra_field2' provided"
        )

    @pytest.mark.parametrize("data_type", SUPPORTED_DATA_TYPES)
    def test_extra_fields_in_columns(self, data_type: str):
        inp = {
            "name": "Test Dataset",
            "fqn": "com.example.TestDataset",
            "description": "This dataset has extra fields not defined in the schema.",
            "columns": [
                {
                    "name": "test_column",
                    "type": data_type,
                    "extra_field": "This should not be here",
                }
            ],
        }
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 1
        assert result["errors"][0]["error_at"] == "$.columns[0].extra_field"
        assert (
            result["errors"][0]["message"]
            == f"'extra_field' invalid attribute for '{data_type}' type"
        )

    def test_missing_fields_at_root(self):
        inp = {
            "name": "Test Dataset",
            "description": "This dataset is missing required fields.",
        }
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 2
        assert result["errors"][0]["error_at"] == "$.fqn"
        assert result["errors"][0]["message"] == "'fqn' attribute missing"
        assert result["errors"][1]["error_at"] == "$.columns"
        assert result["errors"][1]["message"] == "'columns' attribute missing"

    @pytest.mark.parametrize("data_type", SUPPORTED_DATA_TYPES)
    def test_missing_fields_in_columns(self, data_type: str):
        inp = {
            "name": "Test Dataset",
            "fqn": "com.example.TestDataset",
            "description": "This dataset has extra fields not defined in the schema.",
            "columns": [
                {
                    "name": "test_column",
                },
                {
                    "type": data_type,
                },
            ],
        }
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 2
        assert result["errors"][0]["error_at"] == "$.columns[0]"
        assert result["errors"][0]["message"] == "'type' attribute missing"
        assert result["errors"][1]["error_at"] == "$.columns[1].name"
        assert result["errors"][1]["message"] == "'name' attribute missing"

    @pytest.mark.parametrize("value", [[], {}, 1, 0.2, "invalid_type"])
    def test_invalid_data_type(self, value):
        inp = {
            "name": "Test Dataset",
            "fqn": "com.example.TestDataset",
            "description": "This dataset has invalid data types.",
            "columns": [
                {
                    "name": "test_column",
                    "type": value,
                }
            ],
        }
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 1
        assert result["errors"][0]["error_at"] == "$.columns[0].type"
        assert (
            result["errors"][0]["message"]
            == "'type' expected to be one of ['string', 'integer', 'float', 'boolean', 'date', 'datetime']"
        )

    @pytest.mark.parametrize("value", [{}, 100, 0.2, "some_string"])
    def test_invalid_column_type(self, value):
        inp = {
            "name": "Test Dataset",
            "fqn": "com.example.TestDataset",
            "description": "This dataset has invalid data types.",
            "columns": value,
        }
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 1
        assert result["errors"][0]["error_at"] == "$.columns"
        assert result["errors"][0]["message"] == "'columns' expected to be 'list' type"

    @pytest.mark.parametrize("value", [[], 100, 0.2, "some_string"])
    def test_invalid_json_root(self, value):
        inp = value
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 1
        assert result["errors"][0]["error_at"] == "$"
        assert result["errors"][0]["message"] == "'$' expected to be 'object' type"

    @pytest.mark.parametrize("value", [{}, [], 100, 0.2])
    def test_invalid_column_type_in_root(self, value):
        inp = {
            "name": "Test Dataset",
            "fqn": value,
            "description": "This dataset has extra fields not defined in the schema.",
            "columns": [],
        }
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 1
        assert result["errors"][0]["error_at"] == "$.fqn"
        assert result["errors"][0]["message"] == "'fqn' expected to be 'string' type"

    @pytest.mark.parametrize("value", [[], {}, 100, 0.2])
    def test_invalid_column_type_in_columns_for_string(self, value):
        inp = {
            "name": "Test Dataset",
            "fqn": "com.example.TestDataset",
            "description": "Sample Description.",
            "columns": [
                {
                    "name": "test_column",
                    "type": "string",
                    "pattern": value,
                },
                {
                    "name": "test_column_2",
                    "type": "date",
                    "format": value,
                },
                {
                    "name": "test_column_2",
                    "type": "datetime",
                    "format": value,
                },
            ],
        }
        result = validate_schema(inp)
        assert result["valid"] is False
        assert result["error_count"] == 3
        assert result["errors"][0]["error_at"] == "$.columns[0].pattern"
        assert (
            result["errors"][0]["message"] == "'pattern' expected to be 'string' type"
        )
        assert result["errors"][1]["error_at"] == "$.columns[1].format"
        assert result["errors"][1]["message"] == "'format' expected to be 'string' type"
        assert result["errors"][2]["error_at"] == "$.columns[2].format"
        assert result["errors"][2]["message"] == "'format' expected to be 'string' type"

    @pytest.mark.parametrize("value", [[], {}, 0.2, "some_string"])
    def test_invalid_column_type_in_columns_for_integer(self, value):
        inp = {
            "name": "Test Dataset",
            "fqn": "com.example.TestDataset",
            "description": "This dataset has extra fields not defined in the schema.",
            "columns": [
                {
                    "name": "test_column_1",
                    "type": "string",
                    "min_length": value,
                    "max_length": value,
                },
                {
                    "name": "test_column_2",
                    "type": "integer",
                    "minimum": value,
                    "maximum": value,
                },
                {
                    "name": "test_column_3",
                    "type": "float",
                    "precision": value,
                },
            ],
        }

        result = validate_schema(inp)

        assert result["valid"] is False
        assert result["error_count"] == 5

        assert result["errors"][0]["error_at"] == "$.columns[0].max_length"
        assert (
            result["errors"][0]["message"] == "'max_length' expected to be 'int' type"
        )
        assert result["errors"][1]["error_at"] == "$.columns[0].min_length"
        assert (
            result["errors"][1]["message"] == "'min_length' expected to be 'int' type"
        )
        assert result["errors"][2]["error_at"] == "$.columns[1].minimum"
        assert result["errors"][2]["message"] == "'minimum' expected to be 'int' type"
        assert result["errors"][3]["error_at"] == "$.columns[1].maximum"
        assert result["errors"][3]["message"] == "'maximum' expected to be 'int' type"
        assert result["errors"][4]["error_at"] == "$.columns[2].precision"
        assert result["errors"][4]["message"] == "'precision' expected to be 'int' type"

    @pytest.mark.parametrize("value", [[], {}, "some_string"])
    def test_invalid_column_type_in_columns_for_float(self, value):
        inp = {
            "name": "Test Dataset",
            "fqn": "com.example.TestDataset",
            "description": "This dataset has extra fields not defined in the schema.",
            "columns": [
                {
                    "name": "test_column_1",
                    "type": "float",
                    "minimum": value,
                    "maximum": value,
                }
            ],
        }

        result = validate_schema(inp)
        print(result)
        assert result["valid"] is False
        assert result["error_count"] == 2

        assert result["errors"][0]["error_at"] == "$.columns[0].minimum"
        assert result["errors"][0]["message"] == "'minimum' expected to be 'float' type"
        assert result["errors"][1]["error_at"] == "$.columns[0].maximum"
        assert result["errors"][1]["message"] == "'maximum' expected to be 'float' type"
