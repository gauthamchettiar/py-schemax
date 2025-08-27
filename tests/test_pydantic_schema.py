import pytest

from py_schemax.schema.models import DatasetSchema, DataTypeUnion


def test_dataset_schema_with_required_fields_only(dataset_with_reqd_fields):
    """Test that DatasetSchema can be created with only required fields."""
    dataset_schema = DatasetSchema(**dataset_with_reqd_fields)

    # Test required fields are set correctly
    assert dataset_schema.fqn == "namespace.dataset_name"
    assert dataset_schema.name == "Dataset Name"
    assert dataset_schema.version == "1.0"
    assert dataset_schema.columns == []

    # Test optional fields have default values
    assert dataset_schema.description is None
    assert dataset_schema.tags is None
    assert dataset_schema.metadata is None
    assert dataset_schema.depends_on is None
    assert dataset_schema.dependents is None


def test_dataset_schema_with_optional_fields(dataset_with_optional_fields):
    """Test that DatasetSchema correctly handles all optional fields."""
    dataset_schema = DatasetSchema(**dataset_with_optional_fields)

    # Test required fields
    assert dataset_schema.fqn == "namespace.dataset_name"
    assert dataset_schema.name == "Dataset Name"
    assert dataset_schema.version == "1.0"
    assert dataset_schema.columns == []

    # Test optional fields are set correctly
    assert dataset_schema.description == "This is a test dataset schema"
    assert dataset_schema.tags == ["test", "example"]
    assert dataset_schema.metadata == {
        "source": "Generated for testing",
        "frequency": "daily",
    }
    assert dataset_schema.depends_on == ["abc"]
    assert dataset_schema.dependents == ["def"]


def test_dataset_schema_model_dump_field_count(dataset_with_optional_fields):
    """Test that model_dump() returns expected number of fields."""
    dataset_schema = DatasetSchema(**dataset_with_optional_fields)
    # any extra fields added to schema must be added to test, otherwise below assertion will fail
    assert len(dataset_schema.model_dump()) == 9


def test_string_column_type(dataset_with_columns):
    """Test string column type validation and properties."""
    dataset_schema = DatasetSchema(**dataset_with_columns)
    assert dataset_schema.columns is not None
    string_column = dataset_schema.columns[0]

    assert string_column.name == "column1"
    assert string_column.type == "string"
    assert string_column.max_length == 255
    assert string_column.min_length == 1
    assert string_column.pattern == "^[a-zA-Z0-9_]+$"


def test_integer_column_type(dataset_with_columns):
    """Test integer column type validation and properties."""
    dataset_schema = DatasetSchema(**dataset_with_columns)
    assert dataset_schema.columns is not None
    integer_column = dataset_schema.columns[1]

    assert integer_column.name == "column2"
    assert integer_column.type == "integer"
    assert integer_column.minimum == 0
    assert integer_column.maximum == 100


def test_float_column_type(dataset_with_columns):
    """Test float column type validation and properties."""
    dataset_schema = DatasetSchema(**dataset_with_columns)
    assert dataset_schema.columns is not None
    float_column = dataset_schema.columns[2]

    assert float_column.name == "column3"
    assert float_column.type == "float"
    assert float_column.minimum == 0.0
    assert float_column.maximum == 100.0
    assert float_column.precision == 2


def test_boolean_column_type(dataset_with_columns):
    """Test boolean column type validation and properties."""
    dataset_schema = DatasetSchema(**dataset_with_columns)
    assert dataset_schema.columns is not None
    boolean_column = dataset_schema.columns[3]

    assert boolean_column.name == "column4"
    assert boolean_column.type == "boolean"


def test_date_column_type(dataset_with_columns):
    """Test date column type validation and properties."""
    dataset_schema = DatasetSchema(**dataset_with_columns)
    assert dataset_schema.columns is not None
    date_column = dataset_schema.columns[4]

    assert date_column.name == "column5"
    assert date_column.type == "date"
    assert date_column.format == "YYYY-MM-DD"


def test_datetime_column_type(dataset_with_columns):
    """Test datetime column type validation and properties."""
    dataset_schema = DatasetSchema(**dataset_with_columns)
    assert dataset_schema.columns is not None
    datetime_column = dataset_schema.columns[5]

    assert datetime_column.name == "column6"
    assert datetime_column.type == "datetime"
    assert datetime_column.format == "YYYY-MM-DDTHH:mm:ssZ"
    assert datetime_column.timezone == "UTC"


def test_column_common_default_properties(dataset_with_columns):
    """Test that all columns have correct default values for common properties."""
    dataset_schema = DatasetSchema(**dataset_with_columns)

    assert dataset_schema.columns is not None
    for column in dataset_schema.columns:
        assert column.unique is False
        assert column.nullable is True
        assert column.primary_key is False
        assert column.description is None


def test_column_count_and_types(dataset_with_columns):
    """Test that the correct number and types of columns are present."""
    dataset_schema = DatasetSchema(**dataset_with_columns)

    assert dataset_schema.columns is not None
    assert len(dataset_schema.columns) == 6

    column_types = [column.type for column in dataset_schema.columns]
    expected_types = ["string", "integer", "float", "boolean", "date", "datetime"]
    assert column_types == expected_types


def test_column_model_dump_field_counts(dataset_with_columns):
    """Test that each column type has the expected number of fields when dumped."""
    dataset_schema = DatasetSchema(**dataset_with_columns)
    common_column_fields_count = (
        5  # name, type, unique, nullable, primary_key, description
    )

    assert dataset_schema.columns is not None
    # String type: common fields + max_length, min_length, pattern, type = 5 + 4 = 9
    assert dataset_schema.columns[0].type == "string"
    assert len(dataset_schema.columns[0].model_dump()) == common_column_fields_count + 4

    # Integer type: common fields + minimum, maximum, type = 5 + 3 = 8
    assert dataset_schema.columns[1].type == "integer"
    assert len(dataset_schema.columns[1].model_dump()) == common_column_fields_count + 3

    # Float type: common fields + minimum, maximum, precision, type = 5 + 4 = 9
    assert dataset_schema.columns[2].type == "float"
    assert len(dataset_schema.columns[2].model_dump()) == common_column_fields_count + 4

    # Boolean type: common fields + type = 5 + 1 = 6
    assert dataset_schema.columns[3].type == "boolean"
    assert len(dataset_schema.columns[3].model_dump()) == common_column_fields_count + 1

    # Date type: common fields + format, type = 5 + 2 = 7
    assert dataset_schema.columns[4].type == "date"
    assert len(dataset_schema.columns[4].model_dump()) == common_column_fields_count + 2

    # DateTime type: common fields + format, timezone, type = 5 + 3 = 8
    assert dataset_schema.columns[5].type == "datetime"
    assert len(dataset_schema.columns[5].model_dump()) == common_column_fields_count + 3


def test_data_type_union_contains_all_types():
    """Test that DataTypeUnion includes all expected data types."""
    # Verify that all 6 data types are included in the union
    assert len(DataTypeUnion.__args__[0].__args__) == 6  # type: ignore


def test_dataset_schema_disallows_extra_fields_at_root_level(dataset_with_reqd_fields):
    """Test that DatasetSchema rejects extra fields at the root level."""
    with pytest.raises(ValueError, match=r".*Extra inputs are not permitted.*"):
        DatasetSchema(
            **dataset_with_reqd_fields
            | {"abc_invalid_field_xyz": "This should not be allowed"}
        )


def test_column_disallows_extra_fields(dataset_with_reqd_fields):
    """Test that column definitions reject extra fields."""
    with pytest.raises(ValueError, match=r".*Extra inputs are not permitted.*"):
        DatasetSchema(
            **dataset_with_reqd_fields
            | {
                "columns": [
                    {
                        "name": "column1",
                        "type": "string",
                        "description": "A sample column",
                        "abc_invalid_field_xyz": 0,
                    }
                ],
            }
        )
