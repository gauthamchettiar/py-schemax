# Test Fixtures

This directory contains test data files used for testing the py-schemax validation functionality.

## Structure

```
tests/fixtures/
├── valid_schemas/          # Valid schema files that should pass validation
│   ├── example_dataset_schema.yaml  # Comprehensive user dataset example
│   ├── example_product_schema.json  # Product dataset example in JSON
│   ├── minimal_schema.yaml          # Minimal valid schema
│   └── simple_schema.json           # Simple valid schema in JSON
└── invalid_schemas/        # Invalid schema files that should fail validation
    ├── invalid_schema.yaml          # Original invalid schema example
    ├── missing_columns.yaml         # Missing required 'columns' field
    ├── missing_name.json            # Missing required 'name' field
    ├── invalid_types.yaml           # Invalid data types and boolean values
    └── unsupported_format.txt       # Unsupported file format
```

## Usage in Tests

These fixtures can be used in pytest tests like this:

```python
import pytest
from pathlib import Path

# Get fixture paths
FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_SCHEMAS_DIR = FIXTURES_DIR / "valid_schemas"
INVALID_SCHEMAS_DIR = FIXTURES_DIR / "invalid_schemas"

def test_valid_schema():
    schema_path = VALID_SCHEMAS_DIR / "minimal_schema.yaml"
    # Test validation logic here
```

## Adding New Fixtures

When adding new test fixtures:
1. Place valid schemas in `valid_schemas/`
2. Place invalid schemas in `invalid_schemas/`
3. Use descriptive filenames that indicate what the test case covers
4. Support both YAML and JSON formats
5. Update this README with a description of the new fixture
