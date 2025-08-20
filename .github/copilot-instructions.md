# py-schemax Copilot Instructions

## References
- [README.md](../README.md) - includes details related to project.
- [CONTRIBUTING.md](../CONTRIBUTING.md) - guidelines on how to contribute to project.
- [USAGE.md](../USAGE.md) - documentation on how to use CLI tool.

## Core Principals
- **ALWAYS** read README.md and CONTRIBUTING.md before making any changes to project.
- **ALWAYS** use `uv` command for managing project.
- **DO NOT** use `python`, `python3`, `pip` commands. Use `uv run ...`, `uv pip install ...` instead.
- **DO NOT** install any dependencies in global path, create a venv using `uv venv`.
- **DO NOT** push anything to git, always keep everything ready for push and let user decide whether it's okay to push to git.
- **DO NOT** remove any existing test, unless absolutely required and it has been confirmed that corresponding feature has changed or removed.
- **DO NOT** modify `README.md`, `CONTRIBUTING.md` or `USAGE.md` unless explicitly asked for.
- **ALWAYS** update below architecture section when some major functionality change is made to code.

## Architecture

### Project Structure Overview
```
py_schemax/
├── __init__.py              # Package metadata (__version__)
├── cli.py                   # Click-based CLI entry point and command definitions
├── validator.py             # Core validation logic
├── config.py                # Configuration management
├── output.py                # Output control and formatting (text/JSON, verbosity levels)
├── summary.py               # Validation summary tracking and reporting
├── utils.py                 # Utility functions (stdin handling)
└── schema/
    ├── dataset.py          # Pydantic models defining dataset schema structure
    └── validation.py       # TypedDict schemas for validation output format
```

### Core Flow & Components

#### 1. CLI Entry Point (`cli.py`)
- **Purpose**: Click-based CLI interface with main `schemax validate` command
- **Key Functions**:
  - `main()`: Click group with version option
  - `validate()`: Main validation command with extensive CLI options
  - `parse_config_files_for()`: Configuration file parsing callback
- **CLI Options**:
  - Output control: `--out`, `--json`, `--quiet`, `--verbose`, `--silent`
  - Failure modes: `--fail-fast`, `--fail-never`, `--fail-after`
  - Configuration: `--config` flag for custom config files
- **Configuration Support**:
  - Default config files: `schemax.toml`, `pyproject.toml`
  - Environment variables: `SCHEMAX_VALIDATE_*` prefix
  - Precedence: CLI flags > env vars > config files > defaults
- **Flow**: Accepts file paths → parses config → creates Config → validates files → handles output

#### 1a. Configuration Management (`config.py`)
- **Purpose**: Centralized configuration handling with multiple sources
- **Key Functions**:
  - `parse_config_files()`: Parse TOML config files
  - `parse_toml_config_file()`: TOML format parser
- **Key Classes**:
  - `Config`: Main configuration manager
  - `DefaultConfig`: Default values
  - Enums: `OutputFormatEnum`, `OutputLevelEnum`, `FailModeEnum`
- **Configuration Sources** (in precedence order):
  1. CLI flags (highest)
  2. Environment variables (`SCHEMAX_VALIDATE_*`)
  3. Config files (`schemax.toml`, `pyproject.toml`)
  4. Built-in defaults (lowest)

#### 2. Core Validation (`validator.py`)
- **Purpose**: Main validation engine with modular validator classes
- **Key Classes**:
  - `Validator`: Abstract base class for all validators
  - `FileValidator`: Handles file parsing and format validation (JSON/YAML)
  - `PydanticSchemaValidator`: Schema structure validation using Pydantic models
  - `UniqueFQNValidator`: Cross-file FQN uniqueness validation
- **Key Functions**:
  - `validate()`: Main validation method for each validator class
  - `_format_loc_as_jsonql()`: Converts Pydantic error locations to JSONPath format
  - `_format_pydantic_error_as_text()`: Human-readable error message generation
- **Error Handling**: Structured error output with JSONPath-style locations
- **Validation Architecture**: Each validator operates independently and can be combined through the ruleset system

#### 3. Output Control (`output.py`)
- **Purpose**: Centralized output formatting and control
- **Key Classes**:
  - `Output`: Main output controller accepting Config object
- **Output Formats**:
  - Text: Emoji-based (✅❌) with colored output via click.secho
  - JSON: Structured ValidationOutputSchema format

#### 4. Schema Definitions (`schema/dataset.py`)
- **Purpose**: Pydantic models defining the expected dataset schema structure
- **Key Models**:
  - `DatasetSchema`: Root schema model with FQN, name, columns, metadata
  - Data type models: `StringType`, `IntegerType`, `FloatType`, `BooleanType`, `DateType`, `DateTimeType`
  - `DataTypeUnion`: Discriminated union using Pydantic's Discriminator on 'type' field
- **Validation Rules**: Each type has specific constraints (min/max length, patterns, etc.)
- **Configuration**: All models use `model_config = {"extra": "forbid"}` for strict validation

#### 5. Validation Output Schema (`schema/validation.py`)
- **Purpose**: TypedDict definitions for structured validation output
- **Key Schemas**:
  - `ValidationOutputSchema`: Main output structure (file_path, valid, errors, error_count)
  - `ValidationErrorSchema`: Individual error structure (type, error_at, message, pydantic_error)
  - `PydanticErrorSchema`: Stripped Pydantic error details (type, msg)

#### 6. Summary Tracking (`summary.py`)
- **Purpose**: Track validation statistics across multiple files
- **Key Functions**:
  - `add_record()`: Track individual file validation results
  - `to_dict()`: Export summary as dictionary
- **Metrics**: validated_file_count, valid_file_count, invalid_file_count, error_files list

#### 7. Utilities (`utils.py`)
- **Purpose**: Supporting utility functions
- **Key Functions**:
  - `accept_file_paths_as_stdin()`: Handle file paths from stdin for pipe operations

#### 8. Validation Rules System (`rulesets.py`)
- **Purpose**: Modular validation system with configurable rule sets
- **Key Components**:
  - `ValidationRuleSetEnum`: Enumeration of available validation rules
  - `RuleSetBasedValidation`: Main validation orchestrator class
  - `DEFAULT_RULESETS`: Default set of rules applied when no specific rules are specified
- **Available Rules**:
  - `PSX_VAL1` (`PydanticSchemaValidator`): Core schema validation using Pydantic models
  - `PSX_VAL2` (`UniqueFQNValidator`): Cross-file FQN uniqueness validation
- **Rule Control**: CLI flags `--rule-apply` and `--rule-ignore` for selective rule execution
- **Validation Flow**: File format validation always runs first, followed by selected schema validation rules

### Key Design Patterns

#### Configuration Precedence Pattern
- **CLI flags** (highest precedence) > **Environment variables** > **Config files** > **Built-in defaults** (lowest)
- Environment variables use `SCHEMAX_VALIDATE_*` prefix
- Config files support both INI and TOML formats with multiple search locations
- Configuration is centralized in `Config` class with clear setter methods

#### Discriminated Union Schema Pattern
```python
DataTypeUnion = Annotated[
    Union[StringType, IntegerType, FloatType, BooleanType, DateType, DateTimeType],
    Discriminator("type"),
]
```
- Uses Pydantic's Discriminator for type-based validation
- Each data type has a literal 'type' field for discrimination
- Enables extensible schema validation with clear error messages

#### Error Location Formatting
- Converts Pydantic error locations to JSONPath-style format (`$.columns[0].name`)
- Human-readable error messages with context-aware formatting
- Structured error output suitable for both human and machine consumption

#### Output Control Strategy
- Centralized control of output verbosity, format, and failure behavior
- Priority-based option handling (silent > verbose > quiet)
- Dual output formats (emoji-rich text vs structured JSON)

### File Support & Processing
- **Supported Formats**: JSON (`.json`) and YAML (`.yml`, `.yaml`)
- **File Discovery**: Supports stdin for pipe operations (`ls * | schemax validate`)
- **Error Handling**: Graceful handling of missing files, parse errors, unsupported formats

### Testing Architecture
- **Test Structure**: pytest-based with fixtures in `tests/fixtures/`
- **Test Data**: Separate `valid_schemas/` and `invalid_schemas/` directories
- **CLI Testing**: Uses Click's CliRunner for command-line interface testing
- **Multi-version Testing**: nox configuration for Python 3.10-3.13 compatibility
