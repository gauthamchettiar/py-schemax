# 📋 py-schemax

![license MIT](https://img.shields.io/badge/license-MIT-blue) [![codecov](https://codecov.io/gh/gauthamchettiar/py-schemax/branch/main/graph/badge.svg)](https://codecov.io/gh/gauthamchettiar/py-schemax) ![python3.10](https://img.shields.io/badge/python->=3.11-green)

A powerful CLI tool for validating, managing, and maintaining data schema definitions using [Pydantic](https://github.com/pydantic/pydantic) models. This tool helps ensure your data schema files (JSON/YAML) conform to a standardized structure with comprehensive validation rules.

## 🤔 What is this about?

As organizations grow, managing data from diverse sources and formats becomes increasingly complex. py-schemax addresses this challenge by allowing you to define and validate data schemas as YAML or JSON files, making it easy to track and maintain them centrally using version control.

Other similar alternatives,
- [datacontract-cli](https://github.com/datacontract/datacontract-cli): A feature-rich tool for advanced schema management beyond validation.
- [atlas](https://atlasgo.io/): Not a direct match, but useful for schema-as-code workflows.

## ✨ Features

- **Extensible Schema Validation**: Validate JSON and YAML schema files against robust Pydantic models. Easily extend validation rules by updating model attributes—no complex configuration required.
- **Configurable Required Fields**: Control which schema and column attributes are required through configuration files, making validation flexible for different use cases and schema evolution.
- **Unique FQN Validation**: Automatically detect and prevent duplicate Fully Qualified Names (FQNs) across multiple schema files in a single validation run.
- **Schema Dependency Management**: Define and validate dependencies between schema files using `depends_on` and `dependents` fields. Automatically detect circular dependencies to ensure schema integrity.
- **Modular Rule System**: Apply or ignore specific validation rules (`RV_SCHEMA` for schema validation, `RV_UNIQUE_FQN` for unique FQN validation, `RV_DEPENDS_ON`/`RV_DEPENDENTS` for dependency validation) using CLI flags for flexible validation workflows.
- **Clear, Structured Error Reporting**: Detailed error messages with precise [JSONPath](https://jsonpath.com/) style locations and readable formatting make troubleshooting straightforward.
- **Flexible CLI Output & Controls**: Choose between text or JSON output, adjust verbosity, and control exit codes for seamless integration with CI/CD workflows.
- **Multiple Configuration Options**: Support for configuration files (INI/TOML), environment variables, and command-line flags with clear precedence rules.

## 🚀 Getting Started

### 🛠️ Installation

```bash
uv tool install git+https://github.com/gauthamchettiar/py-schemax.git
```

### 💻 Basic Usage

#### Schema Validation
```bash
# Get Help
schemax validate --help

# Validate a multiple files
schemax validate schema1.json schema2.yaml schema3.yml

# Validate all files from a directory
ls * | schemax validate

# Validate with different output options
schemax validate --verbose schema.json     # Prints both OK and ERR records
schemax validate --json schema.json        # JSON output format, for CI/CD
schemax validate --fail-fast schema.json   # Stop on first error, useful for debugging large projects

# Use configuration files or environment variables
schemax validate --config my-config.toml schema.json    # Custom config file
SCHEMAX_VALIDATE_OUTPUT_FORMAT=json schemax validate schema.json  # Environment variable

# Control validation rules
schemax validate --rule-apply RV_SCHEMA schema.json     # Only schema validation
schemax validate --rule-ignore RV_UNIQUE_FQN schema.json    # Skip unique FQN validation
schemax validate --rule-apply RV_DEPENDS_ON schema.json     # Only dependency validation
schemax validate --rule-apply RV_DEPENDENTS schema.json     # Only dependents validation

# See sample configuration files in the repository:
# - sample.schemax.toml, sample.pyproject.toml, sample.env.sh
```

Refer [USAGE.md](/USAGE.md) for more detailed user guide.

### 📄 Example Schema File

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

## 📦 Dependencies
- [`click`](https://github.com/pallets/click) - Command-line interface framework.
- [`pydantic`](https://github.com/pydantic/pydantic) - Data validation using Python type annotations.
- [`pyyaml`](https://github.com/yaml/pyyaml) - YAML parser and emitter.


Want to contribute? Refer [CONTRIBUTING.md](/CONTRIBUTING.md) for a more detailed contribution guide.
