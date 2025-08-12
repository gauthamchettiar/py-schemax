# py-schemax

[![codecov](https://codecov.io/gh/gauthamchettiar/py-schemax/branch/main/graph/badge.svg)](https://codecov.io/gh/gauthamchettiar/py-schemax)

A powerful CLI tool for validating, managing, and maintaining data schema definitions using Pydantic models. This tool helps ensure your data schema files (JSON/YAML) conform to a standardized structure with comprehensive validation rules.

## Features

- **Schema Validation**: Validate JSON and YAML schema files against a predefined pydantic model.
- **Caching**: Built-in caching system for improved performance on repeated validations.
- **Friendly Error Reporting**: Human understandable error messages with JSONPath-style error locations.
- **Customizable CLI Behaviour**: Multiple output formats, flexible output log level, and exit code control.

## Getting Started

### Installation

```bash
uv tool install git+https://github.com/gauthamchettiar/py-schemax.git
```

### Basic Usage

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
```

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

## Dependencies
- [`click`](https://github.com/pallets/click) - Command-line interface framework.
- [`pydantic`](https://github.com/pydantic/pydantic) - Data validation using Python type annotations.
- [`pyyaml`](https://github.com/yaml/pyyaml) - YAML parser and emitter.
- [`cachebox`](https://github.com/awolverp/cachebox) - High-performance caching library, used to cache validation results.
- [`larch-pickle`](https://github.com/kochelmonster/larch-pickle) - Store python objects on disk, used to store objects cached using cachebox to disk.
- [`xxhash`](https://github.com/ifduyue/python-xxhash) - Fast hashing algorithm for cache keys, used for checking file modifications. Changes would be picked from cache or re-computed based on this hash.
