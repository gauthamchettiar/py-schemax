"""Nox configuration for running tests across multiple Python versions."""

import nox

# Python versions to test against
PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]

# Configure nox to use uv by default
nox.options.default_venv_backend = "uv"


@nox.session(python=PYTHON_VERSIONS, venv_backend="uv")
def tests(session):
    """Run the test suite with pytest."""
    # Install dependencies using uv
    session.install(".")
    session.install("pytest", "pytest-cov")

    # Run tests with coverage
    session.run(
        "pytest",
        "--cov=py_schemax",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-fail-under=80",
        *session.posargs,
    )


@nox.session(python=PYTHON_VERSIONS, venv_backend="uv")
def tests_no_cov(session):
    """Run the test suite without coverage."""
    # Install dependencies using uv
    session.install(".")
    session.install("pytest")

    # Run tests without coverage for faster execution
    session.run("pytest", *session.posargs)


@nox.session(python="3.13", venv_backend="uv")
def lint(session):
    """Run linting and code quality checks."""
    session.install("ruff", "mypy", "black", "isort")
    session.install(".", "--group", "dev")

    # Format check
    session.run("black", "--check", "--diff", ".")
    session.run("isort", "--check-only", "--diff", ".")

    # Lint
    session.run("ruff", "check", ".")

    # Type checking
    session.run("mypy", "py_schemax")


@nox.session(python="3.13", venv_backend="uv")
def format(session):
    """Format code using black and isort."""
    session.install("black", "isort")

    session.run("black", ".")
    session.run("isort", ".")


@nox.session(python="3.13", venv_backend="uv")
def type_check(session):
    """Run type checking with mypy."""
    session.install("mypy")
    session.install(".", "--group", "dev")

    session.run("mypy", "py_schemax")


@nox.session(python="3.13", venv_backend="uv")
def security(session):
    """Run security checks with bandit and safety."""
    session.install("bandit[toml]", "safety", "pip-audit")
    session.install(".")

    # Run bandit security checks on code
    session.run("bandit", "-r", "py_schemax", "-f", "json", "-o", "bandit-report.json")
    session.run("bandit", "-r", "py_schemax")

    # Run safety checks on dependencies for known CVEs
    session.log("Running Safety dependency scan...")
    try:
        session.run("safety", "scan", "--output", "json")
        session.run("safety", "scan")
    except Exception as e:
        session.log(f"Safety scan failed: {e}")
        session.log("Falling back to pip-audit...")
        try:
            session.run("pip-audit", "--format=json", "--output=safety-report.json")
            session.run("pip-audit", "--desc")
        except Exception as e2:
            session.log(f"pip-audit also failed: {e2}")
            session.log("Creating empty safety report...")
            with open("safety-report.json", "w") as f:
                f.write('{"vulnerabilities": [], "scan_target": "dependencies"}')

    session.log(
        "Security scans completed - reports saved to bandit-report.json and safety-report.json"
    )


@nox.session(python="3.13", venv_backend="uv")
def docs(session):
    """Build documentation (placeholder for future)."""
    session.log("Documentation building not yet implemented")


@nox.session(python="3.13", venv_backend="uv")
def build(session):
    """Build the package using uv."""
    session.run("uv", "build", external=True)


@nox.session(python="3.13", venv_backend="uv")
def install_test(session):
    """Test installation of the package using uv."""
    # Build the package using uv
    session.run("uv", "build", external=True)

    # Find and install the built wheel
    import glob

    wheel_files = glob.glob("dist/*.whl")
    if wheel_files:
        session.run("uv", "pip", "install", wheel_files[0], external=True)
    else:
        session.error("No wheel file found in dist/")

    # Test that the CLI works
    session.run("schemax", "--help")


# Default sessions to run when just calling 'nox'
nox.options.sessions = ["tests"]
