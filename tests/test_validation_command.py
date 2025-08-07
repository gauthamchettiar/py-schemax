"""Tests for the validate subcommand CLI functionality."""

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from py_schemax.cli import main, validate


def test_valid_files_default_options(valid_schemas):
    """Test validation of valid files with default options."""
    runner = CliRunner()
    result = runner.invoke(validate, [str(path) for path in valid_schemas.values()])

    assert result.exit_code == 0
    assert "Validation completed successfully!" in result.output


def test_invalid_files_default_behavior(invalid_schemas):
    """Test validation of invalid files with default behavior."""
    runner = CliRunner()
    result = runner.invoke(validate, [str(path) for path in invalid_schemas.values()])

    assert result.exit_code != 0
    assert result.output.count("❌") == len(invalid_schemas)


def test_mixed_valid_invalid_files(valid_schemas, invalid_schemas):
    """Test validation with a mix of valid and invalid files."""
    runner = CliRunner()
    mixed_paths = list(valid_schemas.values())[:1] + list(invalid_schemas.values())[:1]
    result = runner.invoke(
        validate, [str(path) for path in mixed_paths] + ["--verbose"]
    )

    # Should exit with error due to invalid files
    assert result.exit_code != 0
    # Should show both success and failure
    assert "✅" in result.output
    assert "❌" in result.output


def test_json_output_format(valid_schemas):
    """Test validation with JSON output format."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]
    result = runner.invoke(validate, [str(schema_path), "--out", "json"])

    assert result.exit_code == 0
    # Verify output contains valid JSON
    lines = result.output.strip().split("\n")
    json_lines = [
        line
        for line in lines
        if line.strip() and not line.strip().startswith("Validation")
    ]
    assert len(json_lines) > 0
    # Should be able to parse as JSON
    for json_line in json_lines:
        json.loads(json_line)


def test_json_flag_override(valid_schemas):
    """Test that --json flag overrides --out option."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]
    result = runner.invoke(validate, [str(schema_path), "--out", "text", "--json"])

    assert result.exit_code == 0
    # Should output JSON despite --out text
    lines = result.output.strip().split("\n")
    json_lines = [
        line
        for line in lines
        if line.strip() and not line.strip().startswith("Validation")
    ]
    assert len(json_lines) > 0


def test_quiet_mode(valid_schemas):
    """Test validation with quiet mode (default behavior)."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]
    result = runner.invoke(validate, [str(schema_path), "--quiet"])

    assert result.exit_code == 0
    # Quiet mode should show minimal output
    assert "Validation completed successfully!" in result.output


def test_verbose_mode(valid_schemas, invalid_schemas):
    """Test validation with verbose mode."""
    runner = CliRunner()
    all_paths = (
        list(valid_schemas.values()) + list(invalid_schemas.values())[:1]
    )  # Mix valid and invalid
    result = runner.invoke(validate, [str(path) for path in all_paths] + ["--verbose"])

    # Should show detailed output for each file
    assert "✅" in result.output  # Valid files
    assert "❌" in result.output  # Invalid files
    for path in all_paths:
        assert str(path) in result.output


def test_silent_mode(valid_schemas):
    """Test validation with silent mode."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]
    result = runner.invoke(validate, [str(schema_path), "--silent"])

    assert result.exit_code == 0
    # Silent mode should produce no output at all
    assert len(result.output.strip()) == 0


def test_fail_fast_mode(invalid_schemas):
    """Test validation with fail-fast mode."""
    runner = CliRunner()
    # Use multiple invalid files
    invalid_paths = list(invalid_schemas.values())[:3]
    result = runner.invoke(
        validate, [str(path) for path in invalid_paths] + ["--fail-fast"]
    )

    assert result.exit_code != 0
    # Should stop on first error, so might not process all files
    error_count = result.output.count("❌")
    assert error_count >= 1


def test_fail_never_mode(invalid_schemas):
    """Test validation with fail-never mode."""
    runner = CliRunner()
    result = runner.invoke(
        validate, [str(path) for path in invalid_schemas.values()] + ["--fail-never"]
    )

    # Should never exit with error code even with invalid files
    assert result.exit_code == 0
    assert result.output.count("❌") == len(invalid_schemas)


def test_no_summary_option(valid_schemas):
    """Test validation with no summary option."""
    runner = CliRunner()
    result = runner.invoke(
        validate, [str(path) for path in valid_schemas.values()] + ["--no-summary"]
    )

    assert result.exit_code == 0
    # Should not show the boxed summary, but will still show completion message
    assert "✅ VALID" not in result.output  # This is part of the boxed summary
    assert "❌ INVALID" not in result.output  # This is part of the boxed summary


def test_summary_override_silent(valid_schemas):
    """Test that --summary overrides --silent."""
    runner = CliRunner()
    result = runner.invoke(
        validate,
        [str(path) for path in valid_schemas.values()] + ["--silent", "--summary"],
    )

    assert result.exit_code == 0
    # Should show summary despite silent flag
    assert "Validation completed successfully!" in result.output


def test_verbose_overrides_quiet(valid_schemas):
    """Test that --verbose overrides --quiet."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]
    result = runner.invoke(validate, [str(schema_path), "--quiet", "--verbose"])

    assert result.exit_code == 0
    # Should show verbose output
    assert "✅" in result.output
    assert str(schema_path) in result.output


def test_silent_overrides_verbose_and_quiet(valid_schemas):
    """Test that --silent overrides both --verbose and --quiet."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]
    result = runner.invoke(
        validate, [str(schema_path), "--quiet", "--verbose", "--silent"]
    )

    assert result.exit_code == 0
    # Should be silent
    assert len(result.output.strip()) == 0 or "✅" not in result.output


def test_empty_file_list():
    """Test validation with no files provided."""
    runner = CliRunner()
    result = runner.invoke(validate, [])

    # Should handle empty input gracefully (no files to validate = success)
    assert result.exit_code == 0
    assert "Validation completed successfully!" in result.output


def test_unsupported_file_format():
    """Test validation with unsupported file format."""
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
        f.write("This is not a schema file")
        temp_path = f.name

    try:
        result = runner.invoke(validate, [temp_path])
        assert result.exit_code != 0
        assert "❌" in result.output
    finally:
        Path(temp_path).unlink()


def test_help_option():
    """Test that help option works for validate command."""
    runner = CliRunner()
    result = runner.invoke(validate, ["--help"])

    assert result.exit_code == 0
    assert "Validate a file against the Defined Schema" in result.output
    assert "FILE_PATHS" in result.output


def test_main_command_help():
    """Test that main command help includes validate subcommand."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "validate" in result.output


def test_version_option():
    """Test that version option works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    # Should show version information
    assert len(result.output.strip()) > 0


@pytest.mark.parametrize("output_format", ["text", "json"])
def test_output_formats(valid_schemas, output_format):
    """Test different output formats."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]
    result = runner.invoke(validate, [str(schema_path), "--out", output_format])

    assert result.exit_code == 0
    if output_format == "json":
        # Should contain JSON output
        lines = result.output.strip().split("\n")
        json_lines = [
            line
            for line in lines
            if line.strip() and not line.strip().startswith("Validation")
        ]
        assert len(json_lines) > 0


def test_multiple_flag_combinations(valid_schemas):
    """Test various flag combinations that should work together."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]

    # Test compatible flag combinations
    test_cases = [
        ["--verbose", "--json"],
        ["--quiet", "--json"],
        ["--fail-never", "--verbose"],
        ["--summary", "--json"],
    ]

    for flags in test_cases:
        result = runner.invoke(validate, [str(schema_path)] + flags)
        assert result.exit_code == 0, f"Failed with flags: {flags}"


def test_priority_of_conflicting_flags(valid_schemas):
    """Test that flag priorities work as expected."""
    runner = CliRunner()
    schema_path = list(valid_schemas.values())[0]

    # Test that higher priority flags override lower priority ones
    # silent > verbose > quiet
    result = runner.invoke(
        validate, [str(schema_path), "--quiet", "--verbose", "--silent"]
    )
    assert result.exit_code == 0
    # Should be silent (minimal output)
    output_lines = [line for line in result.output.split("\n") if line.strip()]
    assert len(output_lines) <= 1  # At most just summary or nothing
