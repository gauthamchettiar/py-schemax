# 📖 Usage Guide

This guide provides comprehensive instructions for using the `schemax` CLI tool to validate data schema definitions.

## Table of Contents

- [Installation](#installation)
- [Basic Commands](#basic-commands)
- [Configuration](#configuration)
- [Schema File Format](#schema-file-format)
- [Validation Examples](#validation-examples)
- [Output Formats](#output-formats)
- [Advanced Options](#advanced-options)
- [Integration with CI/CD](#integration-with-cicd)
- [Troubleshooting](#troubleshooting)

## Installation

### For End Users

Install py-schemax using uv:

```bash
uv tool install git+https://github.com/gauthamchettiar/py-schemax.git
```

### For Development

Clone and run directly:

```bash
git clone https://github.com/gauthamchettiar/py-schemax.git
cd py-schemax
uv sync --group dev
```

Verify the installation:

```bash
schemax --version
# or for development: uv run schemax --version
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

## Configuration

py-schemax supports multiple ways to configure default options, listed in order of precedence (highest to lowest):

1. **Command-line flags** (highest precedence)
2. **Environment variables**
3. **Configuration files**
4. **Built-in defaults** (lowest precedence)

### Configuration Files

py-schemax automatically looks for configuration files in the current directory in this order:

1. `schemax.ini` (INI format)
2. `schemax.toml` (TOML format)
3. `pyproject.toml` (TOML format, under `[tool.schemax.validate]` section)

You can also specify a custom configuration file using the `--config` option.

#### INI Configuration Format

```ini
[schemax.validate]
output_format = "json"
output_level = "verbose"
fail_mode = "after"
```

#### TOML Configuration Format

**In schemax.toml:**
```toml
[schemax.validate]
output_format = "json"
output_level = "verbose"
fail_mode = "after"
```

**In pyproject.toml:**
```toml
[tool.schemax.validate]
output_format = "json"
output_level = "verbose"
fail_mode = "after"
```

#### Configuration Options

| Option | Values | Description |
|--------|--------|-------------|
| `output_format` | `"text"`, `"json"` | Output format for validation results |
| `output_level` | `"silent"`, `"quiet"`, `"verbose"` | Verbosity level |
| `fail_mode` | `"fast"`, `"never"`, `"after"` | When to exit with error code |

### Environment Variables

Set environment variables to configure default behavior:

```bash
# Set output format
export SCHEMAX_VALIDATE_OUTPUT_FORMAT="json"

# Set verbosity level
export SCHEMAX_VALIDATE_OUTPUT_LEVEL="verbose"

# Set failure mode
export SCHEMAX_VALIDATE_FAIL_MODE="never"

# Run validation with environment defaults
schemax validate schema.json
```

#### Supported Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `SCHEMAX_VALIDATE_OUTPUT_FORMAT` | `json`, `text` | Default output format |
| `SCHEMAX_VALIDATE_OUTPUT_LEVEL` | `silent`, `quiet`, `verbose` | Default verbosity level |
| `SCHEMAX_VALIDATE_FAIL_MODE` | `fast`, `never`, `after` | Default failure behavior |

### Configuration Examples

#### Using Custom Config File

```bash
# Create custom configuration
cat > my-config.ini << EOF
[schemax.validate]
output_format = "json"
output_level = "verbose"
fail_mode = "never"
EOF

# Use custom config file
schemax validate --config my-config.ini schema.json
```

#### Multiple Config Files

```bash
# Use multiple config files (first found wins)
schemax validate --config prod.ini --config dev.ini schema.json
```

#### Sample Configuration Files

The repository includes sample configuration files to get you started:

- `sample.schemax.ini` - INI format example
- `sample.schemax.toml` - TOML format example
- `sample.pyproject.toml` - pyproject.toml integration example

Copy and customize these files for your project needs.

#### Override Precedence Example

```bash
# Config file sets json output, but CLI flag overrides to text
echo '[schemax.validate]\noutput_format = "json"' > schemax.ini
schemax validate --out text schema.json  # Uses text output
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

      - name: Validate schemas with config file
        run: |
          # Create CI configuration
          cat > ci-config.toml << EOF
          [schemax.validate]
          output_format = "json"
          output_level = "verbose"
          fail_mode = "after"
          EOF

          find schemas/ -name "*.json" -o -name "*.yaml" | \
          uv tool run schemax validate --config ci-config.toml > validation_results.json

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-results
          path: validation_results.json

  validate-with-env-vars:
    runs-on: ubuntu-latest
    env:
      SCHEMAX_VALIDATE_OUTPUT_FORMAT: "json"
      SCHEMAX_VALIDATE_OUTPUT_LEVEL: "verbose"
      SCHEMAX_VALIDATE_FAIL_MODE: "never"
    steps:
      - uses: actions/checkout@v3
      - name: Install py-schemax
        run: uv tool install git+https://github.com/gauthamchettiar/py-schemax.git
      - name: Validate with env vars
        run: find schemas/ -name "*.json" -o -name "*.yaml" | uv tool run schemax validate
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    environment {
        SCHEMAX_VALIDATE_OUTPUT_FORMAT = 'json'
        SCHEMAX_VALIDATE_OUTPUT_LEVEL = 'verbose'
        SCHEMAX_VALIDATE_FAIL_MODE = 'after'
    }

    stages {
        stage('Install py-schemax') {
            steps {
                sh 'curl -LsSf https://astral.sh/uv/install.sh | sh'
                sh 'uv tool install git+https://github.com/gauthamchettiar/py-schemax.git'
            }
        }

        stage('Create Config') {
            steps {
                sh '''
                    cat > jenkins-config.ini << EOF
[schemax.validate]
output_format = "json"
output_level = "verbose"
fail_mode = "never"
EOF
                '''
            }
        }

        stage('Validate Schemas') {
            steps {
                sh '''
                    find schemas/ -name "*.json" -o -name "*.yaml" | \
                    uv tool run schemax validate --config jenkins-config.ini > validation_results.json
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

## Configuration Summary

py-schemax provides flexible configuration through multiple sources with clear precedence:

### Configuration Methods (in precedence order)

1. **CLI Flags** (highest) - `--json`, `--verbose`, `--fail-fast`, etc.
2. **Environment Variables** - `SCHEMAX_VALIDATE_OUTPUT_FORMAT`, etc.
3. **Configuration Files** - `schemax.ini`, `schemax.toml`, `pyproject.toml`
4. **Built-in Defaults** (lowest) - text output, quiet mode, fail-after

### Quick Reference

| Setting | CLI Flag | Env Variable | Config Key | Values | Default |
|---------|----------|--------------|------------|--------|---------|
| Output Format | `--json`, `--out` | `SCHEMAX_VALIDATE_OUTPUT_FORMAT` | `output_format` | `json`, `text` | `text` |
| Verbosity | `--verbose`, `--silent` | `SCHEMAX_VALIDATE_OUTPUT_LEVEL` | `output_level` | `silent`, `quiet`, `verbose` | `quiet` |
| Failure Mode | `--fail-fast`, `--fail-never` | `SCHEMAX_VALIDATE_FAIL_MODE` | `fail_mode` | `fast`, `never`, `after` | `after` |

### Sample Files

The repository includes ready-to-use sample configuration files:
- `sample.schemax.ini` - INI format
- `sample.schemax.toml` - TOML format
- `sample.pyproject.toml` - Integration with existing pyproject.toml
- `sample.env.sh` - Shell script to set environment variables

Copy and customize these files for your specific needs.

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
| `schemax validate --config custom.ini *.json` | Use custom config file |
| `find . -name "*.json" \| schemax validate` | Validate files from pipe |
