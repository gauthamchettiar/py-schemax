# 📖 Usage Guide

This guide provides comprehensive instructions for using the `schemax` CLI tool to validate data schema definitions.

## Table of Contents

- [Installation](#installation)
- [Basic Commands](#basic-commands)
- [Schema File Format](#schema-file-format)
- [Validation Examples](#validation-examples)
- [Output Formats](#output-formats)
- [Advanced Options](#advanced-options)
- [Integration with CI/CD](#integration-with-cicd)
- [Troubleshooting](#troubleshooting)

## Installation

Install py-schemax using uv:

```bash
uv tool install git+https://github.com/gauthamchettiar/py-schemax.git
```

Verify the installation:

```bash
schemax --version
```

## Basic Commands

### Getting Help

```bash
# General help
schemax --help

# Validation command help
schemax validate --help
```

### Validate Single File

```bash
# Validate a JSON schema file
schemax validate user_schema.json

# Validate a YAML schema file
schemax validate user_schema.yaml
```

### Validate Multiple Files

```bash
# Validate multiple specific files
schemax validate schema1.json schema2.yaml schema3.yml

# Validate all schema files in current directory
schemax validate *.json *.yaml *.yml

# Using pipe for dynamic file discovery
find . -name "*.json" -o -name "*.yaml" | schemax validate
ls schemas/ | schemax validate
```

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

### Example Schema Files

#### Simple JSON Schema

```json
{
  "name": "User Schema",
  "fqn": "users.basic",
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

#### Complex YAML Schema

```yaml
name: "User Dataset"
fqn: "users.complete"
description: "Complete user information dataset"
version: "1.2"
columns:
  - name: "user_id"
    type: "integer"
    nullable: false
    primary_key: true
    description: "Unique user identifier"
    minimum: 1

  - name: "username"
    type: "string"
    nullable: false
    description: "User's unique username"
    min_length: 3
    max_length: 50
    pattern: "^[a-zA-Z0-9_]+$"

  - name: "email"
    type: "string"
    nullable: false
    description: "User's email address"
    max_length: 100

  - name: "age"
    type: "integer"
    nullable: true
    minimum: 0
    maximum: 150

  - name: "height"
    type: "float"
    nullable: true
    minimum: 0.0
    maximum: 3.0
    precision: 2

  - name: "is_active"
    type: "boolean"
    nullable: false
    description: "Account status"

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
  last_updated: "2025-01-31"
  source: "user_management_system"

tags:
  - "user-data"
  - "production"
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
# Validate with default settings (quiet mode)
schemax validate user_schema.json
# Output: ✅ user_schema.json (only if errors occur)

# Validate with verbose output
schemax validate --verbose user_schema.json
# Output: ✅ user_schema.json
```

### Handling Multiple Files

```bash
# Validate multiple files with verbose output
schemax validate --verbose schema1.json schema2.yaml
# Output:
# ✅ schema1.json
# ❌ schema2.yaml

# Stop on first error (fail-fast mode)
schemax validate --fail-fast schema1.json schema2.yaml
# Stops immediately if schema1.json fails
```

### Using Pipes

```bash
# Validate all schema files in a directory
find schemas/ -name "*.json" -o -name "*.yaml" | schemax validate --verbose

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
      "type": "missing",
      "error_at": "$.columns[0].name",
      "message": "Field required",
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
# Quiet mode (default) - only show errors
schemax validate user_schema.json

# Verbose mode - show all results
schemax validate --verbose user_schema.json

# Silent mode - no output, only exit codes
schemax validate --silent user_schema.json

# JSON format (overrides --out option)
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

### Combining Options

```bash
# Verbose JSON output with fail-fast
schemax validate --verbose --json --fail-fast *.json

# Quiet mode (only errors) with never fail (for CI/CD logging)
schemax validate --quiet --fail-never --json schemas/*.yaml > results.json
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
        run: |
          find schemas/ -name "*.json" -o -name "*.yaml" | \
          uv tool run schemax validate --verbose --json --fail-after > validation_results.json

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-results
          path: validation_results.json
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Install py-schemax') {
            steps {
                sh 'curl -LsSf https://astral.sh/uv/install.sh | sh'
                sh 'uv tool install git+https://github.com/gauthamchettiar/py-schemax.git'
            }
        }

        stage('Validate Schemas') {
            steps {
                sh '''
                    find schemas/ -name "*.json" -o -name "*.yaml" | \
                    uv tool run schemax validate --json --verbose > validation_results.json
                '''

                archiveArtifacts artifacts: 'validation_results.json'

                // Parse results for build status
                script {
                    def results = readJSON file: 'validation_results.json'
                    if (!results.valid) {
                        error("Schema validation failed")
                    }
                }
            }
        }
    }
}
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
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

### Performance Tips

#### Caching
py-schemax automatically caches validation results to improve performance:

- Cache is stored in `.schemax/validation.pickle`
- Files are re-validated only when content changes
- Cache persists across runs

#### Clear Cache
```bash
# Remove cache directory to force re-validation
rm -rf .schemax/
```

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
| `find . -name "*.json" \| schemax validate` | Validate files from pipe |
