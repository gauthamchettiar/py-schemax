# py-schemax

A powerful CLI tool for validating, managing, and maintaining data schema definitions using Pydantic models. This tool helps ensure your data schema files (JSON/YAML) conform to a standardized structure with comprehensive validation rules.

## Features

- **Schema Validation**: Validate JSON and YAML schema files against a predefined DatasetSchema model.
- **Caching**: Built-in caching system for improved performance on repeated validations.
- **Batch Processing**: Validate multiple schema files in a single command.
- **Friendly Error Messages**: Comprehensive error reporting with JSONPath-style error locations.
- **Customizable CLI Behaviour**: Multiple output formats, flexible output log level, and exit code control.

## Roadmap
- [ ] A schema can depend on one or more schemas.
- [ ] A column can depend on one or more columns from another schema or same schema.
- [ ] A subset of columns can be inherited from another schema, allowing modularity.

## Schema Structure

The tool validates against a `DatasetSchema` that supports:

### Schema Properties
- `fqn`: Fully qualified name
- `name`: Schema name
- `description`: Schema description
- `version`: Schema version (default: "1.0")
- `columns`: List of column definitions
- `metadata`: Additional key-value metadata
- `tags`: List of tags for categorization
- `inherits`: List of parent schemas to inherit from
- `inherited_by`: List of child schemas

### Column Properties
- `name`: Unique identifier for the column
- `type`: Data type (string, integer, float, boolean, date, datetime)
- `nullable`: Whether null values are allowed (default: true)
- `unique`: Whether values must be unique across the dataset
- `primary_key`: Whether this column is the primary key
- `description`: Human-readable description

### Data Types
- **String**: With optional min/max length, regex patterns
- **Integer**: With optional min/max values
- **Float**: With optional min/max values and precision
- **Boolean**: Simple true/false values
- **Date**: Date-only with customizable format
- **DateTime**: Full timestamp with timezone support


## Installation

### For End Users (CLI Tool Installation)

#### Using uv tool install (Recommended)
```bash
# Install directly from GitHub (once published)
uv tool install git+https://github.com/gauthamchettiar/py-schemax.git

# Or install from local directory
git clone <repository-url>
cd py-schemax
uv tool install .
```

#### Using uv pip install
```bash
# Install from GitHub
uv pip install git+https://github.com/gauthamchettiar/py-schemax.git

# Or install from local directory
git clone <repository-url>
cd py-schemax
uv pip install .
```

### For Developers

#### Using uv (Recommended)
```bash
git clone <repository-url>
cd py-schemax
uv sync --dev  # Install with development dependencies
```

#### Development installation with pip
```bash
git clone <repository-url>
cd py-schemax
pip install -e ".[dev]"
```

## Usage

### Basic Validation
```bash
# Validate a single schema file
schemax validate schema.json

# Validate multiple files
schemax validate schema1.json schema2.yaml schema3.yml
ls * | schemax validate # validate all files in folder
ls **/* | schemax validate # validate all files in folder, recursively
```

### Output Control Options
```bash
# Quiet mode (default) - only show errors and summary
schemax validate --quiet schema1.json schema2.json

# Verbose mode - show detailed progress
schemax validate --verbose schema1.json schema2.json

# Silent mode - suppress all output except exit codes
schemax validate --silent schema1.json  schema2.json

# JSON output format
schemax validate --json schema1.json schema2.json
schemax validate --out json schema1.json schema2.json
```

### Error Handling Options
```bash
# Stop on first error (fail-fast)
ls * | schemax validate --fail-fast

# Never exit with error code (useful for CI)
ls * | schemax validate --fail-never

# Exit with error after processing all files (default)
ls * | schemax validate --fail-after
```

### Summary Control
```bash
# Suppress summary
schemax validate --no-summary schema.json

# Force show only summary (overrides --silent)
schemax validate --silent --summary schema.json
```

### Example Schema Files

**Simple Schema (JSON)**:
```json
{
  "name": "User Schema",
  "fqn": "users.schema",
  "columns": [
    {
      "name": "user_id",
      "type": "integer",
      "nullable": false,
      "primary_key": true
    },
    {
      "name": "username",
      "type": "string",
      "nullable": false,
      "min_length": 3,
      "max_length": 50
    }
  ]
}
```

**Complex Schema (YAML)**:
```yaml
name: "User Dataset"
fqn: "users.complex_schema"
description: "A comprehensive user dataset schema"
version: "1.0"
columns:
  - name: "user_id"
    type: "integer"
    nullable: false
    primary_key: true
    description: "Unique user identifier"
    minimum: 1

  - name: "email"
    type: "string"
    nullable: false
    max_length: 100
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

  - name: "signup_date"
    type: "date"
    nullable: false
    format: "YYYY-MM-DD"

  - name: "last_login"
    type: "datetime"
    nullable: true
    format: "YYYY-MM-DD HH:MM:SS"
    timezone: "UTC"

metadata:
  created_by: "Data Team"
  source: "user_management_system"

tags: ["user", "core", "production"]
```

## Dependencies
- `click` - Command-line interface framework
- `pydantic` - Data validation using Python type annotations
- `pyyaml` - YAML parser and emitter
- `cachebox` - High-performance caching library
- `larch-pickle` - Persistent cache storage
- `xxhash` - Fast hashing algorithm for cache keys, used for checking changed content

## Development

### Testing

This project uses [nox](https://nox.thea.codes/) for running tests across multiple Python versions with [uv](https://docs.astral.sh/uv/) as the package manager.

#### Setup Development Environment
```bash
# Install all development dependencies
uv sync --dev
```

#### Run tests
```bash
# Run tests on all supported Python versions
uv run nox

# Run tests on specific Python version
uv run nox -s tests-3.13

# Run tests without coverage for faster execution
uv run nox -s tests_no_cov

# Run tests with specific pytest arguments
uv run nox -s tests -- -v -k "test_specific"
```

#### Code Quality
```bash
# Run linting and type checking
uv run nox -s lint

# Format code
uv run nox -s format

# Run type checking only
uv run nox -s type_check

# Run security checks
uv run nox -s security
```

#### Pre-commit Hooks
This project uses [pre-commit](https://pre-commit.com/) to ensure code quality before commits:

```bash
# Install pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type pre-push

# Run pre-commit hooks manually on all files
uv run pre-commit run --all-files

# Run hooks on specific files
uv run pre-commit run --files py_schemax/cli.py
```

**Pre-commit hooks include:**
- **Formatting**: Black, isort
- **Linting**: Ruff
- **Type checking**: MyPy
- **Minimal tests**: Fast test run on Python 3.13 (no coverage)

**Pre-push hooks include:**
- **Security checks**: Bandit + Safety (via nox)
- **Full test suite**: All tests across Python versions

#### Build and Install Testing
```bash
# Build the package
uv run nox -s build

# Test package installation
uv run nox -s install_test
```

### Supported Python Versions
- Python 3.11
- Python 3.12
- Python 3.13 (recommended)
