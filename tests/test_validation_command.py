"""Tests for the validate subcommand CLI functionality."""

import json

import pytest
from click.testing import CliRunner

from py_schemax.cli import validate

_VALID_FILE_COUNT = 2
_INVALID_FILE_COUNT = 7


def _validate_text_stdout(
    result, *, expected_exit_code, expected_ok_count, expected_error_count
):
    """Helper function to assert validation results."""
    assert result.exit_code == expected_exit_code
    assert result.stdout.count("✅") == expected_ok_count
    assert result.stdout.count("❌") == expected_error_count


def _validate_json_stdout(
    result, *, expected_exit_code, expected_ok_count, expected_error_count
):
    assert result.exit_code == expected_exit_code
    lines = [line for line in result.stdout.strip().split("\n") if line.strip() != ""]
    assert len(lines) == expected_ok_count + expected_error_count
    actual_ok_count, actual_error_count = 0, 0
    for json_line in lines:
        data = json.loads(json_line)
        if data["valid"]:
            actual_ok_count += 1
        else:
            actual_error_count += 1
    assert actual_ok_count == expected_ok_count
    assert actual_error_count == expected_error_count


def _validate_stdout(
    result,
    output_format,
    *,
    expected_exit_code,
    expected_ok_count,
    expected_error_count,
):
    """Unified helper function to validate output in both text and JSON formats."""
    if output_format == "json":
        _validate_json_stdout(
            result,
            expected_exit_code=expected_exit_code,
            expected_ok_count=expected_ok_count,
            expected_error_count=expected_error_count,
        )
    elif output_format == "text":
        _validate_text_stdout(
            result,
            expected_exit_code=expected_exit_code,
            expected_ok_count=expected_ok_count,
            expected_error_count=expected_error_count,
        )


def _validate_stderr(result, *, expected_exit_code):
    if expected_exit_code == 0:
        assert "Validation completed successfully!" in result.stderr
    else:
        assert "Validation completed with errors!" in result.stderr


def _with_output_format_option(args, output_format) -> list[str]:
    """Inject the output format option into the command arguments."""
    return args + ["--out", output_format]


class TestDefaultBehaviour:
    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_valid_files_default_behaviour(self, valid_schemas, output_format):
        """Test validation of valid files with default options in both text and JSON formats."""
        runner = CliRunner()
        args = [str(path) for path in valid_schemas.values()]

        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format,
            expected_exit_code=0,
            expected_ok_count=0,
            expected_error_count=0,
        )
        _validate_stderr(result, expected_exit_code=0)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_invalid_files_default_behavior(self, invalid_schemas, output_format):
        """Test validation of invalid files with default behavior in both text and JSON formats."""
        runner = CliRunner()
        args = [str(path) for path in invalid_schemas.values()]

        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_mixed_valid_invalid_files_default_behavior(
        self, valid_schemas, invalid_schemas, output_format
    ):
        """Test validation with a mix of valid and invalid files across different output formats and verbosity levels."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ]

        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )
        _validate_stdout(
            result,
            output_format,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)


class TestOutputFormats:
    def test_json_output_format(self, valid_schemas, invalid_schemas):
        """Test validation with JSON output format."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--out", "json"]
        result = runner.invoke(validate, args)

        _validate_json_stdout(
            result,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=_INVALID_FILE_COUNT,
        )

        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--json"]
        result = runner.invoke(validate, args)

        _validate_json_stdout(
            result,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)


class TestOutputLevels:
    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_quiet_mode(self, valid_schemas, invalid_schemas, output_format):
        """Test validation with quiet mode (default behavior)."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--quiet"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_verbose_mode(self, valid_schemas, invalid_schemas, output_format):
        """Test validation with verbose mode."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--verbose"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_silent_mode(self, valid_schemas, invalid_schemas, output_format):
        """Test validation with silent mode."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--silent"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=0,
        )
        _validate_stderr(result, expected_exit_code=1)


class TestFailModes:
    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_fail_after_mode(self, valid_schemas, invalid_schemas, output_format):
        """Test validation with fail-after mode."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--fail-after", "--verbose"]

        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_fail_fast_mode(self, valid_schemas, invalid_schemas, output_format):
        """Test validation with fail-fast mode."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--fail-fast", "--verbose"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=1,
        )
        _validate_stderr(result, expected_exit_code=1)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_fail_never_mode(self, valid_schemas, invalid_schemas, output_format):
        """Test validation with fail-never mode."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--fail-never", "--verbose"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=0,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)


class TestOverrides:
    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_output_level_override_with_silent(
        self, valid_schemas, invalid_schemas, output_format
    ):
        """Test that output level can be overridden by command line options."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--silent", "--verbose", "--quiet"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=0,
        )
        _validate_stderr(result, expected_exit_code=1)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_output_format_override_with_json(
        self, valid_schemas, invalid_schemas, output_format
    ):
        """Test that verbose output level overrides quiet and silent."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--verbose", "--quiet"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_fail_mode_override_with_fail_fast(
        self, valid_schemas, invalid_schemas, output_format
    ):
        """Test that fail-never overrides fail-fast and fail-after."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--fail-fast", "--fail-never", "--fail-after", "--verbose"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=1,
        )
        _validate_stderr(result, expected_exit_code=1)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_fail_mode_override_with_fail_never(
        self, valid_schemas, invalid_schemas, output_format
    ):
        """Test that fail-never overrides fail-fast and fail-never."""
        runner = CliRunner()
        args = [
            str(path)
            for path in list(valid_schemas.values()) + list(invalid_schemas.values())
        ] + ["--fail-never", "--fail-after", "--verbose"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=0,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=_INVALID_FILE_COUNT,
        )
        _validate_stderr(result, expected_exit_code=1)


class TestErrorHandling:
    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_non_existent_file(self, output_format):
        """Test validation with a non-existent file."""
        runner = CliRunner()
        args = ["non_existent_file.json"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=1,
        )
