import pytest

from py_schemax.config import Config
from py_schemax.model import SupportedDataTypes
from py_schemax.validator import (
    DependentsSchemaValidator,
    DependsOnSchemaValidator,
    FileValidator,
    PydanticSchemaValidator,
    UniqueFQNValidator,
)


class TestNonPydanticErrors:
    def test_file_not_found(self, invalid_schemas):
        fv = FileValidator(Config())
        result = fv.validate(invalid_schemas["invalid_missing_file"])
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
        assert fv.validated_content is None

    def test_unsupported_format(self, invalid_schemas):
        fv = FileValidator(Config())
        result = fv.validate(invalid_schemas["invalid_unsupported_format"])
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
        assert fv.validated_content is None

    def test_invalid_json(self, invalid_schemas):
        fv = FileValidator(Config())
        result = fv.validate(invalid_schemas["invalid_json"])
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
        assert fv.validated_content is None

    def test_invalid_yaml(self, invalid_schemas):
        fv = FileValidator(Config())
        result = fv.validate(invalid_schemas["invalid_yaml"])
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
        assert fv.validated_content is None


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
        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")
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

    @pytest.mark.parametrize("data_type", SupportedDataTypes.__members__.keys())
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
        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")
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
        psv = PydanticSchemaValidator(
            Config(model_required_attributes=["fqn", "columns"])
        )
        result = psv.validate(inp, "")
        assert result["valid"] is False
        assert result["error_count"] == 2
        assert result["errors"][0]["error_at"] == "$.fqn"
        assert result["errors"][0]["message"] == "'fqn' attribute missing"
        assert result["errors"][1]["error_at"] == "$.columns"
        assert result["errors"][1]["message"] == "'columns' attribute missing"

    @pytest.mark.parametrize("data_type", SupportedDataTypes.__members__.keys())
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
        psv = PydanticSchemaValidator(
            Config(column_required_attributes={data_type: ["name", "type"]})
        )
        result = psv.validate(inp, "")
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
        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")
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
        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")
        assert result["valid"] is False
        assert result["error_count"] == 1
        assert result["errors"][0]["error_at"] == "$.columns"
        assert result["errors"][0]["message"] == "'columns' expected to be 'list' type"

    @pytest.mark.parametrize("value", [[], 100, 0.2, "some_string"])
    def test_invalid_json_root(self, value):
        inp = value
        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")
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
        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")
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
        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")
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

        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")

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

        psv = PydanticSchemaValidator(Config())
        result = psv.validate(inp, "")
        assert result["valid"] is False
        assert result["error_count"] == 2

        assert result["errors"][0]["error_at"] == "$.columns[0].minimum"
        assert result["errors"][0]["message"] == "'minimum' expected to be 'float' type"
        assert result["errors"][1]["error_at"] == "$.columns[0].maximum"
        assert result["errors"][1]["message"] == "'maximum' expected to be 'float' type"


class TestUniqueFQNValidatorErrors:
    def test_unique_fqn_ok(self):
        ufv = UniqueFQNValidator(Config())
        inputs = [
            {
                "name": "Test Dataset",
                "fqn": f"com.example.TestDataset{i}",
                "description": "This dataset has extra fields not defined in the schema.",
                "columns": [],
            }
            for i in range(5)
        ]
        for inp in inputs:
            result = ufv.validate(inp, "")

            assert result["valid"] is True
            assert result["error_count"] == 0

    def test_duplicate_fqn(self):
        ufv = UniqueFQNValidator(Config())
        inputs = [
            {
                "name": "Test Dataset",
                "fqn": "com.example.TestDataset",
                "description": "This dataset has extra fields not defined in the schema.",
                "columns": [],
            },
            {
                "name": "Test Dataset",
                "fqn": "com.example.TestDataset",
                "description": "This dataset has extra fields not defined in the schema.",
                "columns": [],
            },
        ]
        result1 = ufv.validate(inputs[0], "")
        assert result1["valid"] is True
        assert result1["error_count"] == 0

        result2 = ufv.validate(inputs[1], "")
        assert result2["valid"] is False
        assert result2["error_count"] == 1
        assert result2["errors"][0]["error_at"] == "$.fqn"
        assert (
            result2["errors"][0]["message"]
            == "Duplicate FQN 'com.example.TestDataset', already present at ''"
        )

    def test_missing_fqn(self):
        ufv = UniqueFQNValidator(Config())
        inputs = [
            {
                "name": "Test Dataset",
                "description": "This dataset has extra fields not defined in the schema.",
                "columns": [],
            },
        ]
        result = ufv.validate(inputs[0], "")
        assert result["valid"] is False
        assert result["error_count"] == 1
        assert result["errors"][0]["error_at"] == "$.fqn"
        assert (
            result["errors"][0]["message"]
            == "Duplicate fqn check is enabled but fqn field is missing or invalid"
        )


class TestDependencyValidator:
    def test_valid_dependency_depends_on(self, dependent_schemas):
        fv = FileValidator(Config())
        dv = DependsOnSchemaValidator(Config())

        for schema_file in [
            dependent_schemas["valid_dependency_a"],
            dependent_schemas["valid_dependency_b"],
            dependent_schemas["valid_dependency_c"],
        ]:
            fv.validate(str(schema_file))
            assert fv.validated_content is not None

            result = dv.validate(fv.validated_content, str(schema_file))
            assert result["valid"] is True

    def test_invalid_circular_dependency_depends_on(self, dependent_schemas):
        fv = FileValidator(Config())
        dv = DependsOnSchemaValidator(Config())

        fv.validate(str(dependent_schemas["invalid_dependency_a"]))
        assert fv.validated_content is not None
        result = dv.validate(
            fv.validated_content, str(dependent_schemas["invalid_dependency_a"])
        )
        assert result["valid"] is True

        fv.validate(str(dependent_schemas["invalid_dependency_b"]))
        assert fv.validated_content is not None
        result = dv.validate(
            fv.validated_content, str(dependent_schemas["invalid_dependency_b"])
        )
        assert result["valid"] is True

        fv.validate(str(dependent_schemas["invalid_dependency_c"]))
        assert fv.validated_content is not None
        result = dv.validate(
            fv.validated_content, str(dependent_schemas["invalid_dependency_c"])
        )
        assert result["valid"] is False
        assert result["errors"][0]["type"] == "circular_dependency_detected"

    def test_valid_dependency_dependents(self, dependent_schemas):
        fv = FileValidator(Config())
        dv = DependentsSchemaValidator(Config())

        for schema_file in [
            dependent_schemas["valid_dependency_a"],
            dependent_schemas["valid_dependency_b"],
            dependent_schemas["valid_dependency_c"],
        ]:
            fv.validate(str(schema_file))
            assert fv.validated_content is not None

            result = dv.validate(fv.validated_content, str(schema_file))
            assert result["valid"] is True

    def test_invalid_circular_dependency_dependents(self, dependent_schemas):
        fv = FileValidator(Config())
        dv = DependentsSchemaValidator(Config())

        fv.validate(str(dependent_schemas["invalid_dependency_a"]))
        assert fv.validated_content is not None
        result = dv.validate(
            fv.validated_content, str(dependent_schemas["invalid_dependency_a"])
        )
        assert result["valid"] is True

        fv.validate(str(dependent_schemas["invalid_dependency_b"]))
        assert fv.validated_content is not None
        result = dv.validate(
            fv.validated_content, str(dependent_schemas["invalid_dependency_b"])
        )
        assert result["valid"] is False

    def test_invalid_file_not_present(self):
        input = {
            "name": "Invalid Dependency",
            "description": "This is an invalid dependency schema.",
            "depends_on": [
                "tests/fixtures/dependent_schemas/valid_dependency_b.yaml"
                "non_existent_file.yaml",
            ],
            "dependents": [
                "tests/fixtures/dependent_schemas/valid_dependency_c.yaml",
                "non_existent_file.yaml",
            ],
        }
        dv1 = DependsOnSchemaValidator(Config())
        result = dv1.validate(input, "")
        assert result["valid"] is False
        assert result["errors"][0]["type"] == "dependent_file_not_found"

        dv2 = DependentsSchemaValidator(Config())
        result = dv2.validate(input, "")
        assert result["valid"] is False
        assert result["errors"][0]["type"] == "dependent_file_not_found"

    def test_invalid_field(self):
        inputs = [
            {
                "name": "Invalid Field",
                "depends_on": "tests/fixtures/dependent_schemas/valid_dependency_b.yaml",
                "dependents": [
                    1,
                    "tests/fixtures/dependent_schemas/valid_dependency_b.yaml",
                ],
            },
            {
                "name": "Invalid Field 2",
                "depends_on": [
                    ["tests/fixtures/dependent_schemas/valid_dependency_b.yaml"]
                ],
                "dependents": [
                    1,
                    "tests/fixtures/dependent_schemas/valid_dependency_b.yaml",
                ],
            },
        ]
        dv1 = DependsOnSchemaValidator(Config())
        for input in inputs:
            result = dv1.validate(input, "")
            assert result["valid"] is False
            assert result["errors"][0]["type"] == "invalid_type"

        dv2 = DependentsSchemaValidator(Config())
        for input in inputs:
            result = dv2.validate(input, "")
            assert result["valid"] is False
            assert result["errors"][0]["type"] == "invalid_type"
