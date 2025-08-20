"""Tests for the validate subcommand CLI functionality."""

import json
import tempfile

import pytest
from click.testing import CliRunner

from py_schemax.cli import validate
from py_schemax.config import DEFAULT_CONFIG_FILES

_VALID_FILE_COUNT = 2
_INVALID_FILE_COUNT = 8


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


class TestInputMethods:
    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_accept_file_paths_as_stdin(
        self, valid_schemas, invalid_schemas, output_format
    ):
        """Test that file paths can be provided via stdin when no arguments are given."""
        runner = CliRunner()

        # Prepare file paths as stdin input (one path per line)
        file_paths = list(valid_schemas.values()) + list(invalid_schemas.values())
        stdin_input = "\n".join(str(path) for path in file_paths) + "\n"

        # Run command with no arguments but with stdin input
        result = runner.invoke(
            validate,
            _with_output_format_option(["--verbose"], output_format),
            input=stdin_input,
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
    def test_stdin_with_empty_lines(self, valid_schemas, output_format):
        """Test that empty lines in stdin input are properly ignored."""
        runner = CliRunner()

        # Prepare stdin input with empty lines
        file_paths = list(valid_schemas.values())
        stdin_input = (
            "\n".join(
                [
                    str(file_paths[0]),
                    "",  # empty line
                    "   ",  # whitespace only line
                    str(file_paths[1]),
                    "",  # empty line at end
                ]
            )
            + "\n"
        )

        result = runner.invoke(
            validate,
            _with_output_format_option(["--verbose"], output_format),
            input=stdin_input,
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=0,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=0,
        )
        _validate_stderr(result, expected_exit_code=0)

    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_stdin_input_ignored_when_args_provided(
        self, valid_schemas, invalid_schemas, output_format
    ):
        """Test that stdin input is ignored when file arguments are provided on command line."""
        runner = CliRunner()

        # Prepare valid files as command line arguments
        valid_args = [str(path) for path in valid_schemas.values()]

        # Prepare invalid files as stdin input (should be ignored)
        invalid_stdin = "\n".join(str(path) for path in invalid_schemas.values()) + "\n"

        result = runner.invoke(
            validate,
            _with_output_format_option(valid_args + ["--verbose"], output_format),
            input=invalid_stdin,
        )

        # Should only process the valid files from args, ignoring stdin
        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=0,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=0,
        )
        _validate_stderr(result, expected_exit_code=0)


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
        ] + ["--output-level", "quiet"]
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
        ] + ["--fail-mode", "after", "--verbose"]

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
        ] + ["--silent", "--verbose", "--output-level", "quiet"]
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
        ] + ["--verbose", "--output-level", "quiet"]
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
        ] + ["--fail-fast", "--fail-never", "--fail-mode", "after", "--verbose"]
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
        ] + ["--fail-never", "--fail-mode", "after", "--verbose"]
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
    def test_file_not_found(self, output_format):
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


class TestEnvVariables:
    def test_env_variables_are_accepted_json_verbose(self, valid_schemas):
        runner = CliRunner()
        result = runner.invoke(
            validate,
            [str(path) for path in valid_schemas.values()],
            env={
                "SCHEMAX_VALIDATE_OUTPUT_FORMAT": "json",
                "SCHEMAX_VALIDATE_OUTPUT_LEVEL": "verbose",
                "SCHEMAX_VALIDATE_FAIL_MODE": "after",
            },
        )
        _validate_json_stdout(
            result,
            expected_exit_code=0,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=0,
        )

    def test_env_variables_are_accepted_json_silent(self, invalid_schemas):
        runner = CliRunner()
        result = runner.invoke(
            validate,
            [str(path) for path in invalid_schemas.values()],
            env={
                "SCHEMAX_VALIDATE_OUTPUT_FORMAT": "json",
                "SCHEMAX_VALIDATE_OUTPUT_LEVEL": "silent",
                "SCHEMAX_VALIDATE_FAIL_MODE": "after",
            },
        )
        _validate_json_stdout(
            result,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=0,
        )

    def test_env_variables_are_accepted_text_failnever(self, invalid_schemas):
        runner = CliRunner()
        result = runner.invoke(
            validate,
            [str(path) for path in invalid_schemas.values()],
            env={
                "SCHEMAX_VALIDATE_OUTPUT_FORMAT": "text",
                "SCHEMAX_VALIDATE_FAIL_MODE": "never",
            },
        )
        _validate_text_stdout(
            result,
            expected_exit_code=0,
            expected_ok_count=0,
            expected_error_count=_INVALID_FILE_COUNT,
        )

    def test_env_variables_are_accepted_text_failfast(self, invalid_schemas):
        runner = CliRunner()
        result = runner.invoke(
            validate,
            [str(path) for path in invalid_schemas.values()],
            env={
                "SCHEMAX_VALIDATE_FAIL_MODE": "fast",
            },
        )
        _validate_text_stdout(
            result,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=1,
        )


class TestConfigFile:
    @pytest.mark.parametrize("input_file", DEFAULT_CONFIG_FILES)
    def test_default_config_file_accepted(self, input_file):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open(input_file, "w") as f:
                f.write("[schemax.validate]\n")
                f.write('output_format = "json"\n')
                f.write('output_level = "verbose"\n')
                f.write('fail_mode = "never"\n')

            with open("valid_schema.json", "w") as f:
                json.dump(
                    {
                        "name": "ValidSchema",
                        "fqn": "com.example.ValidSchema",
                        "columns": [],
                    },
                    f,
                )

            result = runner.invoke(
                validate,
                [str("valid_schema.json")],
            )
            _validate_json_stdout(
                result,
                expected_exit_code=0,
                expected_ok_count=1,
                expected_error_count=0,
            )

    def test_default_config_file_accepted_pytoml(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("pyproject.toml", "w") as f:
                f.write("[tool.schemax.validate]\n")
                f.write('output_format = "json"\n')
                f.write('output_level = "verbose"\n')
                f.write('fail_mode = "never"\n')

            with open("valid_schema.json", "w") as f:
                json.dump(
                    {
                        "name": "ValidSchema",
                        "fqn": "com.example.ValidSchema",
                        "columns": [],
                    },
                    f,
                )

            result = runner.invoke(
                validate,
                [str("valid_schema.json")],
            )
            _validate_json_stdout(
                result,
                expected_exit_code=0,
                expected_ok_count=1,
                expected_error_count=0,
            )

    def test_config_file_is_accepted_text_verbose(self, valid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.validate]\n")
            f.write('output_format = "text"\n')
            f.write('output_level = "verbose"\n')
            f.write('fail_mode = "never"\n')

        runner = CliRunner()
        args = [str(path) for path in valid_schemas.values()] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        _validate_text_stdout(
            result,
            expected_exit_code=0,
            expected_ok_count=_VALID_FILE_COUNT,
            expected_error_count=0,
        )

    def test_config_file_is_accepted_text_silent(self, invalid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.validate]\n")
            f.write('output_format = "text"\n')
            f.write('output_level = "silent"\n')
            f.write('fail_mode = "after"\n')

        runner = CliRunner()
        args = [str(path) for path in invalid_schemas.values()] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        _validate_text_stdout(
            result,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=0,
        )

    def test_config_file_is_accepted_json_failnever(self, invalid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.validate]\n")
            f.write('output_format = "json"\n')
            f.write('fail_mode = "never"\n')

        runner = CliRunner()
        args = [str(path) for path in invalid_schemas.values()] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        _validate_json_stdout(
            result,
            expected_exit_code=0,
            expected_ok_count=0,
            expected_error_count=_INVALID_FILE_COUNT,
        )

    def test_config_file_is_accepted_json_failfast(self, invalid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.validate]\n")
            f.write('output_format = "json"\n')
            f.write('fail_mode = "fast"\n')

        runner = CliRunner()
        args = [str(path) for path in invalid_schemas.values()] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        _validate_json_stdout(
            result,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=1,
        )


class TestInvalidConfigFile:
    def test_non_existent_config_file(self, valid_schemas):
        temp_file_path = tempfile.mkdtemp() + "/non_existent_config.toml"
        runner = CliRunner()
        args = [str(path) for path in valid_schemas.values()] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        assert result.exit_code == 2
        assert f"none of the provided config files are valid" in result.stderr

    def test_wo_validation_section(self, valid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.other]\n")
            f.write('output_format = "json"\n')

        runner = CliRunner()
        args = [str(path) for path in valid_schemas.values()] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        assert result.exit_code == 2
        assert f"none of the provided config files are valid" in result.stderr

    def test_invalid_toml_file(self, valid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.validate]\n")
            f.write("invalid_line\n")

        runner = CliRunner()
        args = [str(path) for path in valid_schemas.values()] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        assert result.exit_code == 2


class TestConfigOverrides:
    def test_override_env_over_file(self, invalid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.validate]\n")
            f.write('output_format = "json"\n')
            f.write('output_level = "silent"\n')
            f.write('fail_mode = "never"\n')

        runner = CliRunner()
        args = [str(path) for path in invalid_schemas.values()] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(
            validate,
            args,
            env={
                "SCHEMAX_VALIDATE_OUTPUT_FORMAT": "text",
                "SCHEMAX_VALIDATE_OUTPUT_LEVEL": "verbose",
                "SCHEMAX_VALIDATE_FAIL_MODE": "fast",
            },
        )

        _validate_text_stdout(
            result,
            expected_exit_code=1,
            expected_ok_count=0,
            expected_error_count=1,
        )

    def test_override_options_over_env(self, valid_schemas):
        runner = CliRunner()
        args = [str(path) for path in valid_schemas.values()] + [
            "--out",
            "json",
            "--output-level",
            "silent",
            "--fail-mode",
            "never",
        ]
        result = runner.invoke(
            validate,
            args,
            env={
                "SCHEMAX_VALIDATE_OUTPUT_FORMAT": "text",
                "SCHEMAX_VALIDATE_OUTPUT_LEVEL": "verbose",
                "SCHEMAX_VALIDATE_FAIL_MODE": "fast",
            },
        )

        _validate_json_stdout(
            result,
            expected_exit_code=0,
            expected_ok_count=0,
            expected_error_count=0,
        )


class TestRulesetApplication:
    def test_apply_specific_rules(self, invalid_schemas):
        runner = CliRunner()
        args = [str(invalid_schemas["invalid_columns"])] + [
            "--rule-apply",
            "PSX_VAL1",
        ]
        result = runner.invoke(validate, args)
        assert result.exit_code == 1

    def test_ignore_specific_rules(self, invalid_schemas):
        runner = CliRunner()
        args = [str(invalid_schemas["invalid_columns"])] + [
            "--rule-ignore",
            "PSX_VAL1",
        ]
        result = runner.invoke(validate, args)
        assert result.exit_code == 0

    def test_apply_from_envvars(self, invalid_schemas):
        runner = CliRunner()
        args = [str(invalid_schemas["invalid_columns"])]
        result = runner.invoke(
            validate,
            args,
            env={
                "SCHEMAX_VALIDATE_RULE_APPLY": "PSX_VAL1",
            },
        )
        assert result.exit_code == 1

    def test_ignore_from_envvars(self, invalid_schemas):
        runner = CliRunner()
        args = [str(invalid_schemas["invalid_columns"])]
        result = runner.invoke(
            validate,
            args,
            env={
                "SCHEMAX_VALIDATE_RULE_IGNORE": "PSX_VAL1",
            },
        )
        assert result.exit_code == 0

    def test_apply_from_config_file(self, invalid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.validate]\n")
            f.write('rule_apply = ["PSX_VAL1"]\n')

        runner = CliRunner()
        args = [str(invalid_schemas["invalid_columns"])] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        assert result.exit_code == 1

    def test_ignore_from_config_file(self, invalid_schemas):
        _, temp_file_path = tempfile.mkstemp(suffix="sample_config.toml")
        with open(temp_file_path, "w") as f:
            f.write("[schemax.validate]\n")
            f.write('rule_ignore = ["PSX_VAL1"]\n')

        runner = CliRunner()
        args = [str(invalid_schemas["invalid_columns"])] + [
            "--config",
            temp_file_path,
        ]
        result = runner.invoke(validate, args)
        assert result.exit_code == 0


class TestUniqueFQNValidation:
    @pytest.mark.parametrize("output_format", ["text", "json"])
    def test_unique_fqn_validation(self, valid_schemas, output_format):
        runner = CliRunner()
        args = [
            str(valid_schemas["valid_simple_schema"]),
            str(valid_schemas["valid_simple_schema"]),
        ] + ["--verbose"]
        result = runner.invoke(
            validate, _with_output_format_option(args, output_format=output_format)
        )

        _validate_stdout(
            result,
            output_format=output_format,
            expected_exit_code=1,
            expected_ok_count=1,
            expected_error_count=1,
        )
