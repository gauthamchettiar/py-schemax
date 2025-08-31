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

py-schemax can check for duplicate FQN (Fully Qualified Name) values across all files in a single validation run when the `RV_UNIQUE_FQN` rule is applied:

```bash
# These files would cause a FQN conflict:
# schema1.json: {"name": "Users", "fqn": "com.example.users", "columns": [...]}
# schema2.yaml: {"name": "Customers", "fqn": "com.example.users", "columns": [...]}

schemax validate --rule-apply RV_UNIQUE_FQN schema1.json schema2.yaml
# Output:
# ✅ schema1.json
# ❌ schema2.yaml
#   Error at $.fqn: Duplicate FQN 'com.example.users', already present at 'schema1.json'

# To disable unique FQN validation:
schemax validate --rule-ignore RV_UNIQUE_FQN schema1.json schema2.yaml
# Output:
# ✅ schema1.json
# ✅ schema2.yaml  (FQN conflict ignored)

# To only run unique FQN validation (skip schema validation):
schemax validate --rule-apply RV_UNIQUE_FQN schema1.json schema2.yaml

# Common options
schemax validate --verbose schema.json    # Show all results
schemax validate --json schema.json       # JSON output
schemax validate --fail-fast *.json       # Stop on first error
schemax validate --rule-apply RV_SCHEMA schema.json  # Apply only specific rules
schemax validate --rule-ignore RV_UNIQUE_FQN schema.json # Ignore specific rules

# For comprehensive validation (schema + unique FQN + dependencies):
schemax validate --rule-apply RV_SCHEMA --rule-apply RV_UNIQUE_FQN --rule-apply RV_DEPENDS_ON --rule-apply RV_DEPENDENTS *.json *.yaml
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
| Rule Control | `--rule-apply`, `--rule-ignore` | - | - | `RV_SCHEMA`, `RV_UNIQUE_FQN`, `RV_DEPENDS_ON`, `RV_DEPENDENTS` | `RV_SCHEMA` only |
| Model Required Fields | - | - | `model_required_attributes` | List of field names | `[]` (all optional) |
| Column Required Fields | - | - | `column_required_attributes` | Dict by data type | `{}` (all optional) |

## Schema File Format

py-schemax validates JSON and YAML files against a predefined schema structure. Your schema files must follow this format:

### Required Fields

By default, all fields are optional, but you can configure which fields are required using the `model_required_attributes` and `column_required_attributes` configuration parameters.

**Default Required Fields (if no configuration is provided):**
- **`name`**: Human-readable name for the dataset
- **`fqn`**: Fully qualified name (unique identifier)
- **`columns`**: Array of column definitions

### Optional Fields

- **`description`**: Description of the dataset
- **`version`**: Schema version (default: "1.0")
- **`metadata`**: Additional key-value metadata
- **`tags`**: Array of tags for categorization
- **`depends_on`**: Array of file paths that this schema depends on
- **`dependents`**: Array of file paths that depend on this schema

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
depends_on:
  - common/base_schema.yaml
  - auth/permissions.yaml
dependents:
  - analytics/user_events.yaml
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

## Configurable Required Fields

py-schemax provides flexible control over which fields are required for validation through configuration files. This allows you to customize validation requirements based on your specific use case, project phase, or organizational standards.

### Configuration Parameters

#### `model_required_attributes`
Controls which schema-level fields must be present for validation to pass.

**Available schema-level fields:**
- `name` - Human-readable dataset name
- `fqn` - Fully qualified name (unique identifier)
- `description` - Dataset description
- `version` - Schema version
- `columns` - Array of column definitions
- `metadata` - Additional key-value metadata
- `tags` - Array of categorization tags
- `depends_on` - Array of dependency file paths
- `dependents` - Array of dependent file paths

#### `column_required_attributes`
Controls which fields are required for each column data type. This allows different validation requirements for different column types.

**Available column-level fields (vary by type):**
- Common to all types: `name`, `type`, `nullable`, `unique`, `primary_key`, `description`
- String-specific: `min_length`, `max_length`, `pattern`
- Numeric-specific: `minimum`, `maximum`, `precision` (float only)
- Date/DateTime-specific: `format`, `timezone` (datetime only)

### Configuration Examples

#### Basic Required Fields Configuration

```toml
# schemax.toml or pyproject.toml
[schemax.validate]  # or [tool.schemax.validate]
# Require only essential fields
model_required_attributes = ["name", "fqn", "columns"]

# Require only basic column information
[schemax.validate.column_required_attributes]
string = ["name", "type"]
integer = ["name", "type"]
float = ["name", "type"]
boolean = ["name", "type"]
date = ["name", "type"]
datetime = ["name", "type"]
```

#### Strict Validation Configuration

```toml
# schemax.toml or pyproject.toml
[schemax.validate]  # or [tool.schemax.validate]
# Require comprehensive documentation
model_required_attributes = ["name", "fqn", "description", "version", "columns"]

# Require detailed column specifications
[schemax.validate.column_required_attributes]
string = ["name", "type", "max_length", "nullable"]
integer = ["name", "type", "minimum", "maximum", "nullable"]
float = ["name", "type", "minimum", "maximum", "precision", "nullable"]
boolean = ["name", "type", "nullable"]
date = ["name", "type", "format", "nullable"]
datetime = ["name", "type", "format", "timezone", "nullable"]
```

#### Development vs Production Configuration

```toml
# Development configuration (relaxed)
[schemax.validate]
model_required_attributes = ["name", "columns"]

[schemax.validate.column_required_attributes]
string = ["name", "type"]
integer = ["name", "type"]

# Production configuration (strict)
[schemax.validate]
model_required_attributes = ["name", "fqn", "description", "columns"]

[schemax.validate.column_required_attributes]
string = ["name", "type", "max_length", "nullable"]
integer = ["name", "type", "minimum", "maximum", "nullable"]
```

### Usage Examples

#### Validate with Custom Requirements

```bash
# Use specific configuration file
schemax validate --config strict-config.toml schema.json

# Configuration takes precedence over defaults
schemax validate schema.json  # Uses schemax.toml or pyproject.toml if present
```

#### Schema Evolution Workflow

```toml
# Phase 1: Initial development (minimal requirements)
model_required_attributes = ["name", "columns"]

# Phase 2: Schema stabilization (add documentation)
model_required_attributes = ["name", "fqn", "description", "columns"]

# Phase 3: Production ready (comprehensive validation)
model_required_attributes = ["name", "fqn", "description", "version", "columns"]
```

### Validation Behavior

#### Missing Required Fields
When a required field is missing, validation fails with a clear error message:

```bash
schemax validate schema.json
# ❌ schema.json
#   Error at $.description: Field required
```

#### Different Requirements by Type
Column requirements can vary by data type:

```yaml
# This would fail if max_length is required for strings
columns:
  - name: username
    type: string
    # missing max_length if required

  - name: age
    type: integer
    minimum: 0
    maximum: 150
    # valid if only minimum/maximum required for integers
```

### Best Practices

1. **Start Minimal**: Begin with basic requirements and gradually add more as schemas mature
2. **Environment-Specific**: Use different configurations for development, staging, and production
3. **Type-Appropriate**: Configure column requirements based on the specific needs of each data type
4. **Team Standards**: Align required fields with your organization's data documentation standards
5. **Incremental Adoption**: Use flexible requirements to support gradual schema improvement

## Dependency Management

py-schemax supports defining and validating dependencies between schema files using the `depends_on` and `dependents` fields. This feature helps maintain schema integrity by ensuring dependencies exist and detecting circular dependencies.

### Dependency Fields

#### `depends_on` Field
Specifies a list of file paths that the current schema depends on. These files must exist for validation to pass.

```yaml
name: User Events Schema
fqn: analytics.user_events
depends_on:
  - schemas/common/base_schema.yaml
  - schemas/user/user_schema.yaml
columns:
  - name: event_id
    type: string
  - name: user_id
    type: integer
```

#### `dependents` Field
Specifies a list of file paths that depend on the current schema. This is useful for documentation and maintaining schema relationships.

```yaml
name: Base Schema
fqn: common.base
dependents:
  - schemas/user/user_schema.yaml
  - schemas/analytics/user_events.yaml
columns:
  - name: created_at
    type: datetime
  - name: updated_at
    type: datetime
```

### Dependency Validation Rules

py-schemax provides specific validation rules for dependency management:

- **`RV_DEPENDS_ON`**: Validates that all files listed in `depends_on` exist and checks for circular dependencies
- **`RV_DEPENDENTS`**: Validates that all files listed in `dependents` exist and checks for circular dependencies

### Validation Behavior

#### File Existence Validation
All file paths specified in `depends_on` and `dependents` must exist:

```bash
# This will fail if any dependency file doesn't exist
schemax validate schema_with_dependencies.yaml
```

**Error Output:**
```
❌ schema_with_dependencies.yaml
  Error at $.depends_on: File 'missing_schema.yaml' provided in 'depends_on' field not found
```

#### Circular Dependency Detection
py-schemax automatically detects circular dependencies within the dependency graph:

```yaml
# schema_a.yaml
name: Schema A
fqn: example.schema_a
depends_on:
  - schema_b.yaml

# schema_b.yaml
name: Schema B
fqn: example.schema_b
depends_on:
  - schema_a.yaml  # Creates circular dependency
```

**Error Output:**
```
❌ schema_a.yaml
  Error at $.depends_on: circular dependency present: CycleError('nodes are in a cycle')
```

### Dependency Validation Examples

#### Validate Only Dependencies
```bash
# Validate only depends_on relationships
schemax validate --rule-apply RV_DEPENDS_ON schemas/*.yaml

# Validate only dependents relationships
schemax validate --rule-apply RV_DEPENDENTS schemas/*.yaml

# Skip dependency validation
schemax validate --rule-ignore RV_DEPENDS_ON --rule-ignore RV_DEPENDENTS schemas/*.yaml
```

#### Complex Dependency Structure
```yaml
# base_schema.yaml
name: Base Schema
fqn: common.base
columns:
  - name: id
    type: integer
    primary_key: true
dependents:
  - user_schema.yaml
  - product_schema.yaml

# user_schema.yaml
name: User Schema
fqn: users.schema
depends_on:
  - base_schema.yaml
columns:
  - name: username
    type: string
dependents:
  - user_events_schema.yaml

# user_events_schema.yaml
name: User Events Schema
fqn: analytics.user_events
depends_on:
  - base_schema.yaml
  - user_schema.yaml
columns:
  - name: event_type
    type: string
```

#### Validation Output
```bash
schemax validate --verbose base_schema.yaml user_schema.yaml user_events_schema.yaml
```

**Success Output:**
```
✅ base_schema.yaml
✅ user_schema.yaml
✅ user_events_schema.yaml
```

### Best Practices for Dependencies

1. **Use Relative Paths**: Use relative file paths for portability across environments
2. **Avoid Deep Nesting**: Keep dependency chains shallow to reduce complexity
3. **Document Relationships**: Use both `depends_on` and `dependents` for complete relationship mapping
4. **Validate Early**: Run dependency validation in CI/CD to catch issues early
5. **Organize by Domain**: Group related schemas to minimize cross-domain dependencies

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

# Silent mode - suppresses validation output, summary messages still go to stderr
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
| `RV_SCHEMA` | **Pydantic Schema Validation** - Validates schema structure, data types, constraints, and required fields according to the defined Pydantic models |
| `RV_UNIQUE_FQN` | **Unique FQN Validation** - Ensures that Fully Qualified Names (FQNs) are unique across all validated schema files within a single validation run |
| `RV_DEPENDS_ON` | **Dependency Validation** - Validates that all files listed in `depends_on` exist and checks for circular dependencies |
| `RV_DEPENDENTS` | **Dependents Validation** - Validates that all files listed in `dependents` exist and checks for circular dependencies |

#### Rule Control Options

```bash
# Apply only specific rules (ignores default rule set)
schemax validate --rule-apply RV_SCHEMA schema.json
# Only runs Pydantic schema validation

# Ignore specific rules (applies all other rules)
schemax validate --rule-ignore RV_SCHEMA schema.json
# Skips Pydantic validation (currently would only validate file format)

# Combine multiple rules (when more rules are available)
schemax validate --rule-apply RV_SCHEMA --rule-apply RV_UNIQUE_FQN schema.json
schemax validate --rule-ignore RV_SCHEMA --rule-ignore RV_UNIQUE_FQN schema.json

# Apply dependency validation rules
schemax validate --rule-apply RV_DEPENDS_ON schema.json
schemax validate --rule-apply RV_DEPENDENTS schema.json

# Rule precedence: --rule-apply takes precedence over defaults
# If --rule-apply is specified, only those rules are applied
# If --rule-ignore is specified, those rules are excluded from the default set
```

#### Rule Behavior Examples

```bash
# Default behavior (all rules applied)
schemax validate schema.json
# Runs: File format validation + RV_SCHEMA (Pydantic validation only)

# Apply only schema validation
schemax validate --rule-apply RV_SCHEMA schema.json
# Runs: File format validation + RV_SCHEMA only

# Apply only unique FQN validation
schemax validate --rule-apply RV_UNIQUE_FQN schema.json
# Runs: File format validation + RV_UNIQUE_FQN only

# Apply only dependency validation
schemax validate --rule-apply RV_DEPENDS_ON schema.json
# Runs: File format validation + RV_DEPENDS_ON only

# Apply only dependents validation
schemax validate --rule-apply RV_DEPENDENTS schema.json
# Runs: File format validation + RV_DEPENDENTS only

# Skip schema validation (validate only file format)
schemax validate --rule-ignore RV_SCHEMA schema.json
# Runs: File format validation only

# Skip unique FQN validation (validate only file format and schema)
schemax validate --rule-ignore RV_UNIQUE_FQN schema.json
# Runs: File format validation + RV_SCHEMA only

# Skip dependency validation
schemax validate --rule-ignore RV_DEPENDS_ON --rule-ignore RV_DEPENDENTS schema.json
# Runs: File format validation + RV_SCHEMA only
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
schemax validate --rule-apply RV_SCHEMA --json --verbose *.json

# Skip specific rules with fail-fast behavior
schemax validate --rule-ignore RV_SCHEMA --fail-fast schemas/*.yaml

# Apply only dependency validation with JSON output
schemax validate --rule-apply RV_DEPENDS_ON --rule-apply RV_DEPENDENTS --json schemas/*.yaml

# Complex combination: JSON output, verbose mode, custom rules, never fail
schemax validate --json --verbose --rule-apply RV_SCHEMA --fail-never schemas/
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
schemax validate --rule-apply RV_UNIQUE_FQN incomplete_schema.json
# ❌ incomplete_schema.json
#   Error at $.fqn: Duplicate fqn check is enabled but fqn field is missing
```

**Solution:** When using unique FQN validation (RV_UNIQUE_FQN), ensure all schema files have an `fqn` field defined.

#### Dependency File Not Found
```bash
schemax validate schema_with_dependencies.yaml
# ❌ schema_with_dependencies.yaml
#   Error at $.depends_on: File 'missing_schema.yaml' provided in 'depends_on' field not found
```

**Solution:** Ensure all files listed in `depends_on` and `dependents` fields exist at the specified paths.

#### Circular Dependency Errors
```bash
schemax validate schema_a.yaml schema_b.yaml
# ❌ schema_a.yaml
#   Error at $.depends_on: circular dependency present: CycleError('nodes are in a cycle')
```

**Solution:** Review dependency relationships and remove circular references. Use dependency validation tools to identify the cycle.

### Performance Tips

#### Large File Sets
For validating many files:

```bash
# Use fail-fast to stop on first error
find schemas/ -name "*.json" | schemax validate --fail-fast

# Use silent mode to suppress validation output (summary still goes to stderr)
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
| `schemax validate --silent file.json` | Suppress validation output, summary to stderr |
| `schemax validate --config custom.toml *.json` | Use custom config file |
| `schemax validate --rule-apply RV_SCHEMA file.json` | Apply only specific validation rules |
| `schemax validate --rule-ignore RV_UNIQUE_FQN file.json` | Ignore specific validation rules |
| `schemax validate --rule-apply RV_DEPENDS_ON file.json` | Apply only dependency validation |
| `schemax validate --rule-apply RV_DEPENDENTS file.json` | Apply only dependents validation |
| `find . -name "*.json" \| schemax validate` | Validate files from pipe |

## Configuration Examples

| Configuration | Description |
|---------------|-------------|
| `model_required_attributes = ["name", "fqn"]` | Require only name and fqn fields at schema level |
| `column_required_attributes.string = ["name", "type", "max_length"]` | Require name, type, and max_length for string columns |
| `column_required_attributes.integer = ["name", "type", "minimum", "maximum"]` | Require constraints for integer columns |
