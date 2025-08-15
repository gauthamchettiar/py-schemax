# Contributing to py-schemax

Thank you for your interest in contributing to py-schemax! This document provides comprehensive instructions for setting up your development environment and contributing to the project.

## Table of Contents

- [Project Overview](#project-overview)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Architecture Guidelines](#architecture-guidelines)
- [Git Workflow](#git-workflow)
- [Release Process](#release-process)

## Project Overview

py-schemax is a CLI tool for validating data schema definitions (JSON/YAML) against Pydantic models. It features:

- Comprehensive CLI options for different output formats
- Support for Python 3.10+ across multiple versions
- Comprehensive test suite with 80% minimum coverage requirement

### Key Technologies

- **Build System**: uv (fast Python package manager) + hatchling
- **Testing**: pytest with nox for multi-version testing
- **Code Quality**: black, isort, ruff, mypy, bandit, safety
- **CLI**: Click framework

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gauthamchettiar/py-schemax.git
   cd py-schemax
   ```

2. **Create and activate a virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the project in development mode**:
   ```bash
   uv sync --group dev
   ```

4. **Set up pre-commit hooks**:
   ```bash
   uv run pre-commit install
   uv run pre-commit install --hook-type pre-push
   ```

5. **Verify installation**:
   ```bash
   uv run schemax --help
   ```

## Development Workflow

### Daily Development

1. **Run tests (frequently)**:
   ```bash
   # Quick test run (current Python version)
   uv run pytest

   # Full test suite (all Python versions)
   uv run nox
   ```

2. **Check code quality (before commit)**:
   ```bash
   # Auto-format code
   uv run nox -s format

   # Run all quality checks
   uv run nox -s lint
   ```

## Testing

### Test Structure

- **Test Location**: `tests/` directory
- **Fixtures**: `tests/fixtures/{valid_schemas,invalid_schemas}/` for test data
- **Coverage**: Minimum 80% required (try to keep it at 100%)
- **Multi-version**: Tests run on Python 3.10, 3.11, 3.12, and 3.13

### CLI Testing Pattern

Use Click's CliRunner for command testing:

```python
from click.testing import CliRunner
from py_schemax.cli import validate

def test_cli_command():
    runner = CliRunner()
    result = runner.invoke(validate, ["schema.json", "--verbose"])
    assert result.exit_code == 0
    assert "✅" in result.output
```

### Test Fixtures

- Use existing fixtures in `tests/fixtures/` for consistent test data
- Create new fixtures following the existing pattern:
  - `valid_schemas/` - Schemas that should pass validation
  - `invalid_schemas/` - Schemas that should fail validation

## Code Quality

### Automated Tools

All code quality tools are configured in `pyproject.toml` and run via nox:

```bash
# Run all quality checks
uv run nox -s lint

# Auto-format code
uv run nox -s format

# Security scanning
uv run nox -s security
```

### Tool Configuration

- **Black**: Code formatting (88 character line length)
- **isort**: Import sorting (black profile)
- **Ruff**: Fast linting and additional formatting
- **MyPy**: Static type checking with strict settings
- **Bandit**: Security vulnerability scanning
- **Safety/pip-audit**: Dependency vulnerability scanning (with fallback)

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit:

- Code formatting (black, isort, ruff)
- Type checking (mypy)
- Basic file checks (trailing whitespace, yaml/json syntax)
- Minimal test suite (Python 3.13 only, fast)

Pre-push hooks run on every push:

- Full test suite across all Python versions
- Security scans (bandit + safety)

## Architecture Guidelines

### Core Flow

1. **CLI Entry** (`py_schemax/cli.py`) - Click-based CLI with `schemax validate` command
2. **Validation** (`py_schemax/validator.py`) - Core validation logic
3. **Schema Models** (`py_schemax/schema/dataset.py`) - Pydantic models defining schema structure
4. **Output Control** (`py_schemax/output.py`) - Manages output formats and verbosity

**Key Points**:
- Validation logic handles JSON and YAML files
- File validation includes graceful error handling
- Always validate against Pydantic schema models

### Schema Definition Patterns

- **Discriminated Unions**: Use Pydantic discriminators for type variants
- **Type Safety**: All schemas use `model_config = {"extra": "forbid"}`
- **Validation Output**: Structured via TypedDict schemas

### Error Handling Conventions

- **Structured Errors**: Follow `ValidationErrorSchema` with JSONPath-style locations
- **File Errors**: Handle at validator level (missing files, parse errors)
- **Exit Codes**: Non-zero for validation failures unless `--fail-never` specified

### Output Management

- **OutputControl Class**: Centralized verbosity, format, and failure mode management
- **Dual Formats**: Text (with emojis ✅❌) and structured JSON
- **Summary System**: Built-in success/failure statistics

## Git Workflow

### Branch Strategy

- `main` - Stable releases (current default branch)
- Feature branches convention - `feature/your-feature-name`
- Bugfix branches convention - `bugfix/issue-description`

### Commit Guidelines

1. **Write clear commit messages**:
   ```
   feat: add support for new data types

   - Add support for decimal and timestamp types
   - Update schema validation for new types
   - Add comprehensive test coverage
   ```
2. Use following commit prefixes -
    - feat: for introducing a new feature (not FEATURE or FEATURE:)
    - fix: for a bug fix (not BUGFIX or BUGFIX:)
    - docs: for documentation changes
    - style: for code formatting, not affecting logic
    - refactor: for code changes that neither fix a bug nor add a feature
    - test: for adding or updating tests
    - chore: for routine tasks like dependency upgrades or build changes
    - perf: for performance improvements
    - build: for build system or dependency changes
    - ci: for continuous integration/configuration changes
    - revert: to indicate a commit that reverts a previous change

3. **Keep commits atomic** - one logical change per commit

4. **Test before committing** - make sure to [install pre-commit hooks](#development-setup) will enforce this

### Pull Request Process

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**:
   ```bash
   # Make your changes
   uv run nox  # Run all tests
   uv run nox -s lint  # Check code quality
   ```

3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request** with:
   - Clear description of changes
   - Reference to any related issues
   - Test results showing all checks pass

## Release Process

### Version Management

- Version is defined in `pyproject.toml`
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version before creating release

### Build and Distribution

```bash
# Build the package
uv run nox -s build

# Test installation
uv run nox -s install_test

# Verify CLI works
schemax --help
```

### Release Checklist

1. ✅ All tests pass across all Python versions
2. ✅ Code quality checks pass
3. ✅ Security scans pass
4. ✅ Documentation is up to date
5. ✅ Version number updated in `pyproject.toml`
6. ✅ Build succeeds
7. ✅ Installation test passes

## Troubleshooting

### Common Issues

**Tests failing on specific Python version**:
```bash
# Check specific version
uv run nox -s tests-3.11
```


**Type checking errors**:
```bash
# Run mypy with verbose output
uv run mypy py_schemax --verbose
```

**Pre-commit hook failures**:
```bash
# Run hooks manually
uv run pre-commit run --all-files
```

### Getting Help

- Check existing issues on GitHub
- Review test failures in CI/CD
- Examine the existing codebase for patterns
- Run with verbose output for debugging

## Additional Resources

- [Project README](README.md)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Click Documentation](https://click.palletsprojects.com/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [nox Documentation](https://nox.thea.codes/)

Happy contributing! 🚀
