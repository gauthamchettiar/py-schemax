# Contributing to py-schemax

Thank you for contributing! This guide covers setup, development workflow, and project guidelines.

## Quick Start

**Prerequisites**: Python 3.10+ and [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/gauthamchettiar/py-schemax.git
cd py-schemax
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync --group dev
uv run pre-commit install && uv run pre-commit install --hook-type pre-push
uv run schemax --help  # Verify installation
```

## Technologies

- **Build**: uv + hatchling | **Testing**: pytest + nox | **Quality**: black, isort, ruff, mypy, bandit, safety | **CLI**: Click

## Development Workflow

```bash
# Test frequently
uv run pytest              # Quick test (current Python)
uv run nox                 # Full test suite (all Python versions)

# Before committing
uv run nox -s format       # Auto-format code
uv run nox -s lint         # Quality checks
uv run nox -s security     # Security scans
```

## Testing & Quality

- **Tests**: `tests/` directory with fixtures in `tests/fixtures/{valid_schemas,invalid_schemas}/`
- **Coverage**: 80% minimum (aim for 100%)
- **Multi-version**: Python 3.10-3.13 via nox
- **CLI Testing**: Use Click's CliRunner

```python
from click.testing import CliRunner
from py_schemax.cli import validate

def test_cli_command():
    runner = CliRunner()
    result = runner.invoke(validate, ["schema.json", "--verbose"])
    assert result.exit_code == 0
    assert "✅" in result.output
```

**Quality Tools** (configured in `pyproject.toml`):
- **Black**: 88-char line length | **isort**: black profile | **Ruff**: fast linting
- **MyPy**: strict type checking | **Bandit/Safety**: security scanning

## Architecture Guidelines

### Core Flow

1. **CLI Entry** (`py_schemax/cli.py`) - Click-based CLI with `schemax validate` command
2. **Configuration** (`py_schemax/config.py`) - Configuration management with precedence
3. **Validation** (`py_schemax/validator.py`) - Core validation logic
4. **Schema Models** (`py_schemax/schema/dataset.py`) - Pydantic models defining schema structure
5. **Output Control** (`py_schemax/output.py`) - Manages output formats and verbosity

**Key Points**:
- Configuration precedence: CLI flags > environment variables > config files > defaults
- Supported config files: `schemax.ini`, `schemax.toml`, `pyproject.toml`
- Environment variables use `SCHEMAX_VALIDATE_*` prefix
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
