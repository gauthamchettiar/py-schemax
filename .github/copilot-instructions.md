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
├── validator.py             # Core validation logic with persistent caching
├── cache.py                 # Persistent caching system using larch-pickle + cachebox
├── output.py                # Output control and formatting (text/JSON, verbosity levels)
├── summary.py               # Validation summary tracking and reporting
├── utils.py                 # Utility functions (file hashing, stdin handling)
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
- **CLI Options**:
  - Output control: `--out`, `--json`, `--quiet`, `--verbose`, `--silent`
  - Failure modes: `--fail-fast`, `--fail-never`, `--fail-after`
- **Flow**: Accepts file paths → creates OutputControl → validates files → handles output

#### 2. Core Validation (`validator.py`)
- **Purpose**: Main validation engine with persistent caching
- **Key Functions**:
  - `validate_schema_file()`: Entry point with `@persistent_cachedmethod` decorator
  - `validate_schema()`: Core Pydantic validation logic
  - `_format_loc_as_jsonql()`: Converts Pydantic error locations to JSONPath format
  - `_format_pydantic_error_as_text()`: Human-readable error message generation
- **Caching Strategy**: Uses file hash (xxhash) for cache invalidation
- **Error Handling**: Structured error output with JSONPath-style locations

#### 3. Persistent Caching System (`cache.py`)
- **Purpose**: High-performance caching with disk persistence
- **Key Components**:
  - `persistent_cachedmethod()`: Decorator combining cachebox + larch-pickle
  - Automatic cache loading on startup from `.schemax_cache/validation.pickle`
  - `atexit.register()` for automatic cache saving on program exit
- **Cache Storage**: `.schemax_cache/validation.pickle` file in working directory
- **Cache Backend**: LRUCache(maxsize=10000) from cachebox library

#### 4. Output Control (`output.py`)
- **Purpose**: Centralized output formatting and control
- **Key Classes**:
  - `OutputControl`: Main controller with enums for format/level/fail modes
  - `OutputFormatEnum`: JSON vs TEXT output formats
  - `OutputLevelEnum`: SILENT/QUIET/VERBOSE levels
  - `FailModeEnum`: FAIL_FAST/FAIL_NEVER/FAIL_AFTER modes
- **Output Formats**:
  - Text: Emoji-based (✅❌) with colored output via click.secho
  - JSON: Structured ValidationOutputSchema format

#### 5. Schema Definitions (`schema/dataset.py`)
- **Purpose**: Pydantic models defining the expected dataset schema structure
- **Key Models**:
  - `DatasetSchema`: Root schema model with FQN, name, columns, metadata
  - Data type models: `StringType`, `IntegerType`, `FloatType`, `BooleanType`, `DateType`, `DateTimeType`
  - `DataTypeUnion`: Discriminated union using Pydantic's Discriminator on 'type' field
- **Validation Rules**: Each type has specific constraints (min/max length, patterns, etc.)
- **Configuration**: All models use `model_config = {"extra": "forbid"}` for strict validation

#### 6. Validation Output Schema (`schema/validation.py`)
- **Purpose**: TypedDict definitions for structured validation output
- **Key Schemas**:
  - `ValidationOutputSchema`: Main output structure (file_path, valid, errors, error_count)
  - `ValidationErrorSchema`: Individual error structure (type, error_at, message, pydantic_error)
  - `PydanticErrorSchema`: Stripped Pydantic error details (type, msg)

#### 7. Summary Tracking (`summary.py`)
- **Purpose**: Track validation statistics across multiple files
- **Key Functions**:
  - `add_record()`: Track individual file validation results
  - `to_dict()`: Export summary as dictionary
- **Metrics**: validated_file_count, valid_file_count, invalid_file_count, error_files list

#### 8. Utilities (`utils.py`)
- **Purpose**: Supporting utility functions
- **Key Functions**:
  - `accept_file_paths_as_stdin()`: Handle file paths from stdin for pipe operations
  - `get_hash_of_file()`: xxhash-based file content hashing for cache invalidation

### Key Design Patterns

#### Persistent Caching Pattern
```python
@persistent_cachedmethod(".schemax_cache/validation.pickle", LRUCache(maxsize=10000))
def validate_schema_file(path: str | Path, file_hash: str | None):
    # Validation logic here
```
- Cache persists across program runs using larch-pickle
- File content changes detected via xxhash
- Automatic cache directory creation (`.schemax_cache/`)
- atexit handler ensures cache is saved on program termination

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
- **Hash-based Caching**: Uses xxhash for fast file change detection

### Testing Architecture
- **Test Structure**: pytest-based with fixtures in `tests/fixtures/`
- **Test Data**: Separate `valid_schemas/` and `invalid_schemas/` directories
- **CLI Testing**: Uses Click's CliRunner for command-line interface testing
- **Multi-version Testing**: nox configuration for Python 3.10-3.13 compatibility
