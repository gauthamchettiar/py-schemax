# 📖 Usage Guide

Complete guide for using the `schemax` CLI tool to validate data schema definitions.

## Quick Start

```bash
# Install
uv tool install git+https://github.com/gauthamchettiar/py-schemax.git

# Validate files
schemax validate schema.json              # Single file
schemax validate *.json *.yaml            # Multiple files
# Validate files matching a pattern
ls *_schema.* | schemax validate
```

### Unique FQN Validation

When validating multiple files, py-schemax automatically checks for duplicate FQN (Fully Qualified Name) values across all files in a single validation run:

```bash
# These files would cause a FQN conflict:
# schema1.json: {"name": "Users", "fqn": "com.example.users", "columns": [...]}
# schema2.yaml: {"name": "Customers", "fqn": "com.example.users", "columns": [...]}

schemax validate schema1.json schema2.yaml
# Output:
# ✅ schema1.json
# ❌ schema2.yaml
#   Error at $.fqn: Duplicate FQN 'com.example.users', already present at 'schema1.json'

# To disable unique FQN validation:
schemax validate --rule-ignore PSX_VAL2 schema1.json schema2.yaml
# Output:
# ✅ schema1.json
# ✅ schema2.yaml  (FQN conflict ignored)

# To only run unique FQN validation (skip schema validation):
schemax validate --rule-apply PSX_VAL2 schema1.json schema2.yaml

# Common options
schemax validate --verbose schema.json    # Show all results
schemax validate --json schema.json       # JSON output
schemax validate --fail-fast *.json       # Stop on first error
schemax validate --rule-apply PSX_VAL1 schema.json  # Apply only specific rules
schemax validate --rule-ignore PSX_VAL2 schema.json # Ignore specific rules
```

## Configuration

Configuration precedence (highest to lowest): **CLI flags** → **Environment variables** → **Config files** → **Built-in defaults**

### Config Files
Auto-detected: `schemax.toml`, `pyproject.toml` (or use `--config custom.toml`)

```toml
# schemax.toml or pyproject.toml
[tool.schemax.validate]
output_format = "json"
output_level = "verbose"
fail_mode = "after"
```

### Environment Variables
```bash
export SCHEMAX_VALIDATE_OUTPUT_FORMAT="json"
export SCHEMAX_VALIDATE_OUTPUT_LEVEL="verbose"
export SCHEMAX_VALIDATE_FAIL_MODE="never"
```

### Quick Reference
| Setting | CLI Flag | Env Variable | Config Key | Values | Default |
|---------|----------|--------------|------------|--------|---------|
| Output Format | `--json`, `--out` | `SCHEMAX_VALIDATE_OUTPUT_FORMAT` | `output_format` | `json`, `text` | `text` |
| Verbosity | `--verbose`, `--silent` | `SCHEMAX_VALIDATE_OUTPUT_LEVEL` | `output_level` | `silent`, `quiet`, `verbose` | `quiet` |
| Failure Mode | `--fail-fast`, `--fail-never` | `SCHEMAX_VALIDATE_FAIL_MODE` | `fail_mode` | `fast`, `never`, `after` | `after` |
| Rule Control | `--rule-apply`, `--rule-ignore` | - | - | `PSX_VAL1`, `PSX_VAL2` | All rules applied |

## Schema File Format

py-schemax validates JSON and YAML files against a predefined schema structure. Your schema files must follow this format:

### Required Fields

- **`name`**: Human-readable name for the dataset
- **`fqn`**: Fully qualified name (unique identifier)
- **`columns`**: Array of column definitions

### Optional Fields

- **`description`**: Description of the dataset
- **`version`**: Schema version (default: "1.0")
- **`metadata`**: Additional key-value metadata
- **`tags`**: Array of tags for categorization

### Example Schema File

```yaml
name: User Schema
fqn: users.schema
columns:
  - name: user_id
    type: integer
    nullable: false
    primary_key: true
  - name: username
    type: string
    nullable: false
    min_length: 3
    max_length: 50
```

### Supported Data Types

#### String Type
```yaml
- name: "username"
  type: "string"
  nullable: false          # Optional: default true
  min_length: 3           # Optional: minimum string length
  max_length: 50          # Optional: maximum string length
  pattern: "^[a-zA-Z]+$"  # Optional: regex pattern
```

#### Integer Type
```yaml
- name: "age"
  type: "integer"
  nullable: true
  minimum: 0              # Optional: minimum value
  maximum: 150            # Optional: maximum value
```

#### Float Type
```yaml
- name: "height"
  type: "float"
  nullable: true
  minimum: 0.0            # Optional: minimum value
  maximum: 3.0            # Optional: maximum value
  precision: 2            # Optional: decimal precision
```

#### Boolean Type
```yaml
- name: "is_active"
  type: "boolean"
  nullable: false
```

#### Date Type
```yaml
- name: "birth_date"
  type: "date"
  nullable: true
  format: "YYYY-MM-DD"    # Optional: date format
```

#### DateTime Type
```yaml
- name: "created_at"
  type: "datetime"
  nullable: false
  format: "YYYY-MM-DD HH:MM:SS"  # Optional: datetime format
  timezone: "UTC"                # Optional: timezone
```

### Common Column Properties

All column types support these properties:

- **`name`** (required): Column identifier
- **`type`** (required): Data type (string, integer, float, boolean, date, datetime)
- **`nullable`** (optional): Whether column allows null values (default: true)
- **`unique`** (optional): Whether values must be unique (default: false)
- **`primary_key`** (optional): Whether this is a primary key (default: false)
- **`description`** (optional): Human-readable description

## Validation Examples

### Basic Validation

```bash
schemax validate user_schema.json
```

### Handling Multiple Files

```bash
# passing as arguments
# Validate multiple files with verbose output
schemax validate --verbose schema1.json schema2.yaml
# Output:
# ✅ schema1.json
# ❌ schema2.yaml

# Stop on first error (fail-fast mode)
schemax validate --fail-fast schema1.json schema2.yaml
# Stops immediately if schema1.json fails

# using pipes
# Validate all schema files in a directory
find schemas/ -name "*.json" -o -name "*.yaml" | schemax validate

# Validate files matching a pattern
ls user_*.json | schemax validate --json
```

## Output Formats

### Text Output (Default)

Text output uses emojis and colors for easy reading:

```bash
schemax validate --verbose user_schema.json
```

**Success Output:**
```
✅ user_schema.json
```

**Error Output:**
```
❌ user_schema.json
  Error at $.columns[0].name: Field required
  Error at $.fqn: String should have at least 1 characters
```

### JSON Output

JSON output provides structured data for programmatic processing:

```bash
schemax validate --json user_schema.json
```

**Success Output:**
```json
{
  "file_path": "user_schema.json",
  "valid": true,
  "errors": [],
  "error_count": 0
}
```

**Error Output:**
```json
{
  "file_path": "user_schema.json",
  "valid": false,
  "errors": [
    {
      "type": "validation_error",
      "error_at": "$.name",
      "message": "'name' attribute missing",
      "pydantic_error": {
        "type": "missing",
        "msg": "Field required"
      }
    }
  ],
  "error_count": 1
}
```

## Advanced Options

### Output Control

```bash
# Quiet mode (default) - shows summary and errors only
schemax validate user_schema.json

# Verbose mode - show all results with file-by-file status
schemax validate --verbose user_schema.json

# Silent mode - still shows summary message, only exit codes differ
schemax validate --silent user_schema.json

# JSON format
schemax validate --json user_schema.json

# Explicit output format
schemax validate --out json user_schema.json
schemax validate --out text user_schema.json
```

### Failure Modes

```bash
# Default: fail after all validations (--fail-after)
schemax validate schema1.json schema2.json
# Validates all files, then exits with error code if any failed

# Fail fast: stop on first error
schemax validate --fail-fast schema1.json schema2.json
# Stops immediately when first file fails

# Never fail: always exit with code 0
schemax validate --fail-never schema1.json schema2.json
# Useful for CI/CD when you want to collect all results
```

### Validation Rules Control

py-schemax uses a modular validation system with different rule sets that can be selectively applied or ignored.

#### Available Validation Rules

| Rule ID | Description |
|---------|-------------|
| `PSX_VAL1` | **Pydantic Schema Validation** - Validates schema structure, data types, constraints, and required fields according to the defined Pydantic models |
| `PSX_VAL2` | **Unique FQN Validation** - Ensures that Fully Qualified Names (FQNs) are unique across all validated schema files within a single validation run |

#### Rule Control Options

```bash
# Apply only specific rules (ignores default rule set)
schemax validate --rule-apply PSX_VAL1 schema.json
# Only runs Pydantic schema validation

# Ignore specific rules (applies all other rules)
schemax validate --rule-ignore PSX_VAL1 schema.json
# Skips Pydantic validation (currently would only validate file format)

# Combine multiple rules (when more rules are available)
schemax validate --rule-apply PSX_VAL1 --rule-apply PSX_VAL2 schema.json
schemax validate --rule-ignore PSX_VAL1 --rule-ignore PSX_VAL2 schema.json

# Rule precedence: --rule-apply takes precedence over defaults
# If --rule-apply is specified, only those rules are applied
# If --rule-ignore is specified, those rules are excluded from the default set
```

#### Rule Behavior Examples

```bash
# Default behavior (all rules applied)
schemax validate schema.json
# Runs: File format validation + PSX_VAL1 (Pydantic validation) + PSX_VAL2 (Unique FQN validation)

# Apply only schema validation
schemax validate --rule-apply PSX_VAL1 schema.json
# Runs: File format validation + PSX_VAL1 only

# Apply only unique FQN validation
schemax validate --rule-apply PSX_VAL2 schema.json
# Runs: File format validation + PSX_VAL2 only

# Skip schema validation (validate only file format and unique FQN)
schemax validate --rule-ignore PSX_VAL1 schema.json
# Runs: File format validation + PSX_VAL2 only

# Skip unique FQN validation (validate only file format and schema)
schemax validate --rule-ignore PSX_VAL2 schema.json
# Runs: File format validation + PSX_VAL1 only
```

**Note**: File format validation (JSON/YAML parsing) always runs first regardless of rule settings. Rule control applies to the schema validation layer.

### Combining Options

```bash
# Verbose JSON output with fail-fast
schemax validate --verbose --json --fail-fast *.json

# Quiet mode (only errors) with never fail (for CI/CD logging)
schemax validate --quiet --fail-never --json --verbose schemas/*.yaml > results.json

# Use custom config with CLI override
schemax validate --config ci.toml --fail-fast *.json

# Environment variable with CLI override
export SCHEMAX_VALIDATE_OUTPUT_FORMAT="text"
schemax validate --json schema.json  # Uses JSON despite env var

# Selective rule application with output control
schemax validate --rule-apply PSX_VAL1 --json --verbose *.json

# Skip specific rules with fail-fast behavior
schemax validate --rule-ignore PSX_VAL1 --fail-fast schemas/*.yaml

# Complex combination: JSON output, verbose mode, custom rules, never fail
schemax validate --json --verbose --rule-apply PSX_VAL1 --fail-never schemas/
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Schema Validation
on: [push, pull_request]

jobs:
  validate-schemas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install py-schemax
        run: uv tool install git+https://github.com/gauthamchettiar/py-schemax.git
      - name: Validate schemas
        run: find schemas/ -name "*.json" -o -name "*.yaml" | uv tool run schemax validate --json > results.json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: schema-validation
        name: Validate Schema Files
        entry: uv tool run schemax validate --fail-fast
        language: system
        files: '\.(json|ya?ml)$'
        pass_filenames: true
```


## Troubleshooting

### Common Issues

#### File Not Found
```bash
schemax validate non_existent.json
# ❌ a.json
#     - $ : 'a.json' not found
```

**Solution:** Check file path and ensure file exists.

#### Invalid JSON/YAML Syntax
```bash
schemax validate invalid_syntax.json
# ❌ tests/fixtures/invalid_schemas/invalid_yaml.yaml
#     - $ : error parsing file
```

**Solution:** Validate JSON/YAML syntax using a linter or online validator.

#### Schema Validation Errors
```bash
schemax validate user_schema.json
# ❌ user_schema.json
#   Error at $.columns[0].type: Input should be 'string', 'integer', 'float', 'boolean', 'date' or 'datetime'
```

**Solution:** Check supported data types and fix the schema definition.

#### Missing Required Fields
```bash
schemax validate incomplete_schema.json
# ❌ incomplete_schema.json
#   Error at $.fqn: Field required
#   Error at $.columns: Field required
```

**Solution:** Add all required fields (`name`, `fqn`, `columns`).

#### Duplicate FQN Errors
```bash
schemax validate schema1.json schema2.json
# ✅ schema1.json
# ❌ schema2.json
#   Error at $.fqn: Duplicate FQN 'com.example.dataset', already present at 'schema1.json'
```

**Solution:** Ensure each schema file has a unique `fqn` value across all files being validated in a single run.

#### Missing FQN for Unique Validation
```bash
schemax validate --rule-apply PSX_VAL2 incomplete_schema.json
# ❌ incomplete_schema.json
#   Error at $.fqn: Duplicate fqn check is enabled but fqn field is missing
```

**Solution:** When using unique FQN validation (PSX_VAL2), ensure all schema files have an `fqn` field defined.

### Performance Tips

#### Large File Sets
For validating many files:

```bash
# Use fail-fast to stop on first error
find schemas/ -name "*.json" | schemax validate --fail-fast

# Use silent mode for better performance in scripts
find schemas/ -name "*.json" | schemax validate --silent --json > results.json
```

### Debugging

#### Enable Verbose Output
```bash
schemax validate --verbose problematic_schema.json
```

#### Use JSON Output for Detailed Errors
```bash
schemax validate --json problematic_schema.json | jq '.'
```

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/gauthamchettiar/py-schemax/issues)
- **Documentation**: Check [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md)
- **CLI Help**: Use `schemax --help` or `schemax validate --help`

## Quick Reference

| Command | Description |
|---------|-------------|
| `schemax validate file.json` | Validate single file |
| `schemax validate --verbose *.json` | Validate multiple files with details |
| `schemax validate --json file.yaml` | Get JSON output |
| `schemax validate --fail-fast *.json` | Stop on first error |
| `schemax validate --fail-never *.yaml` | Never exit with error code |
| `schemax validate --silent file.json` | No output, only exit codes |
| `schemax validate --config custom.toml *.json` | Use custom config file |
| `schemax validate --rule-apply PSX_VAL1 file.json` | Apply only specific validation rules |
| `schemax validate --rule-ignore PSX_VAL2 file.json` | Ignore specific validation rules |
| `find . -name "*.json" \| schemax validate` | Validate files from pipe |
