"""Main CLI module for py-schemax."""

from typing import Any, Callable, List, MutableMapping

import click

from py_schemax import __version__
from py_schemax.config import (
    DEFAULT_CONFIG_FILES,
    Config,
    FailModeEnum,
    LogConfig,
    LogLevelEnum,
    OutputFormatEnum,
    OutputLevelEnum,
    parse_config_files,
)
from py_schemax.output import Output
from py_schemax.rulesets import (
    DEFAULT_RULESETS,
    RuleSetBasedValidation,
    ValidationRuleSetEnum,
)
from py_schemax.utils import accept_file_paths_as_stdin

IGNORE_KEYS_FROM_CONFIG = [
    "use_json",  # set using output_format
    "output_level_verbose",  # set using output_level
    "output_level_silent",  # set using output_level
    "fail_fast",  # set using fail_mode
    "fail_never",  # set using fail_mode
    "enable_debug_logging",  # set using log_level
]


def parse_config_files_for(
    section_name: str,
) -> Callable[[click.Context, click.Parameter, List[str]], None]:
    """Parse the config file for a specific command."""

    def _parse(
        ctx: click.Context, param: click.Parameter, file_paths: List[str]
    ) -> None:
        default_map: MutableMapping[str, Any] = ctx.default_map or {}
        from_file_path, parsed_config = parse_config_files(file_paths, section_name)

        default_map.update(parsed_config)
        if not default_map and list(file_paths) != list(DEFAULT_CONFIG_FILES):
            raise click.BadParameter(
                f"none of the provided config files are valid - {file_paths}"
            )
        default_map = {
            k: v for k, v in default_map.items() if k not in IGNORE_KEYS_FROM_CONFIG
        }
        ctx.default_map = default_map

    return _parse


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """A powerful CLI tool for validating, managing, and maintaining data schema definitions using Pydantic models.

    py-schemax helps ensure your data schema files (JSON/YAML) conform to a standardized
    structure with comprehensive validation rules. It provides clear, structured error
    reporting and flexible output options for seamless integration with CI/CD workflows.

    \b
    Examples:
      schemax validate schema.json                    # Validate single file
      schemax validate *.json *.yaml                  # Validate multiple files
      find . -name "*.json" | schemax validate        # Validate from pipe
      schemax validate --json --verbose schemas/      # JSON output with details

    Use 'schemax COMMAND --help' for more information on a command.
    """
    pass  # pragma: no cover


@main.command()
@click.argument("file_paths", nargs=-1, type=click.Path())
@click.option(
    "--config",
    type=click.Path(dir_okay=False),
    default=DEFAULT_CONFIG_FILES,
    multiple=True,
    callback=parse_config_files_for("validate"),
    is_eager=True,
    expose_value=False,
    help="Read option defaults from the specified INI/TOML file.",
    show_default=True,
)
@click.option(
    "--out",
    "output_format",
    type=click.Choice([e.value for e in OutputFormatEnum]),
    help="Output format for validation results",
    envvar="SCHEMAX_VALIDATE_OUTPUT_FORMAT",
)
@click.option(
    "--json",
    "use_json",
    is_flag=True,
    help="Output results in JSON format, overrides --out option",
)
@click.option(
    "--output-level",
    "output_level",
    type=click.Choice([e.value for e in OutputLevelEnum]),
    help="Output level for validation results",
    envvar="SCHEMAX_VALIDATE_OUTPUT_LEVEL",
)
@click.option(
    "--verbose",
    "output_level_verbose",
    is_flag=True,
    help="Show detailed validation progress with ok and errors, overrides --quiet",
)
@click.option(
    "--silent",
    "output_level_silent",
    is_flag=True,
    help="Suppress all output, only exit with error codes, overrides --quiet and --verbose",
)
@click.option(
    "--fail-mode",
    "fail_mode",
    type=click.Choice([e.value for e in FailModeEnum]),
    help="Failure mode for validation",
    envvar="SCHEMAX_VALIDATE_FAIL_MODE",
)
@click.option(
    "--fail-never",
    "fail_never",
    is_flag=True,
    help="Never exit with error code, useful for CI, overrides --fail-fast",
)
@click.option(
    "--fail-fast",
    "fail_fast",
    is_flag=True,
    help="Stop on first validation error, overrides --fail-never and --fail-after",
)
@click.option(
    "--rule-apply",
    "rule_apply",
    type=click.Choice([e.name for e in ValidationRuleSetEnum]),
    multiple=True,
    help="Apply validation rules, only specified rules will be applied",
    envvar="SCHEMAX_VALIDATE_RULE_APPLY",
)
@click.option(
    "--rule-ignore",
    "rule_ignore",
    type=click.Choice([e.name for e in ValidationRuleSetEnum]),
    multiple=True,
    help="Ignore validation rules, only specified rules will be ignored",
    envvar="SCHEMAX_VALIDATE_RULE_IGNORE",
)
@click.option(
    "--log-level",
    "log_level",
    type=click.Choice([e.value for e in LogLevelEnum]),
    help="Set logging level",
    envvar="SCHEMAX_LOG_LEVEL",
)
@click.option(
    "--debug",
    "enable_debug_logging",
    is_flag=True,
    help="Enable debug logging, equivalent to --log-level DEBUG",
)
@click.option(
    "--log-file",
    "enable_file_logging",
    is_flag=True,
    help="Enable logging to file",
    envvar="SCHEMAX_ENABLE_FILE_LOGGING",
)
@click.option(
    "--log-file-path",
    "log_file_path",
    type=click.Path(),
    help="Path to log file (default: schemax.log)",
    envvar="SCHEMAX_LOG_FILE_PATH",
)
@click.pass_context
def validate(
    ctx: click.Context,
    file_paths: List[str],
    output_format: str,
    use_json: bool,
    output_level: str,
    output_level_verbose: bool,
    output_level_silent: bool,
    fail_mode: str,
    fail_fast: bool,
    fail_never: bool,
    rule_apply: tuple[str, ...],
    rule_ignore: tuple[str, ...],
    log_level: str,
    enable_debug_logging: bool,
    enable_file_logging: bool,
    log_file_path: str,
) -> None:
    """Validate schema files against the defined Pydantic data model structure.

    This command validates JSON and YAML schema files to ensure they conform to the
    standardized structure with proper data types, constraints, and required fields.
    Supports validating single files, multiple files, or files from stdin (pipe).

    \b
    FILE_PATHS: One or more paths to JSON (.json) or YAML (.yaml/.yml) schema files.
                If no paths provided, will read file paths from stdin (useful with pipes).

    \b
    Examples:
      # Validate single file
      schemax validate user_schema.json

      # Validate multiple files with detailed output
      schemax validate --verbose schema1.json schema2.yaml

      # Get JSON output for programmatic processing
      schemax validate --json *.json

      # Stop on first error (useful for debugging)
      schemax validate --fail-fast schemas/*.yaml

      # Validate all files but never exit with error code (CI/CD friendly)
      schemax validate --fail-never --json schemas/

      # Validate files from pipe (directory listing)
      find schemas/ -name "*.json" | schemax validate --verbose

      # Silent validation (only exit codes, no output)
      schemax validate --silent schema.json && echo "All valid!"

    \b
    Exit Codes:
      0    All files are valid (or --fail-never used)
      1    One or more files failed validation
      2    Command error (invalid arguments, file not found, etc.)

    \b
    Output Formats:
      Text (default): Human-readable with emojis (✅ success, ❌ error) and colors
      JSON:           Structured data with detailed error information and locations

    \b
    Environment Variables:
      SCHEMAX_VALIDATE_OUTPUT_FORMAT    Set default output format (json|text)
      SCHEMAX_VALIDATE_OUTPUT_LEVEL     Set default verbosity (silent|quiet|verbose)
      SCHEMAX_VALIDATE_FAIL_MODE        Set default failure mode (fail_fast|fail_never|fail_after)
      SCHEMAX_LOG_LEVEL                 Set default logging level (TRACE|DEBUG|INFO|WARNING|ERROR)
      SCHEMAX_ENABLE_FILE_LOGGING       Enable logging to file (true|false)
      SCHEMAX_LOG_FILE_PATH             Set log file path (default: schemax.log)
    """
    file_paths = accept_file_paths_as_stdin(file_paths)

    default_map = ctx.default_map or {}
    config = Config(
        output_format=output_format,
        use_json=use_json,
        output_level=output_level,
        output_level_verbose=output_level_verbose,
        output_level_silent=output_level_silent,
        fail_mode=fail_mode,
        fail_fast=fail_fast,
        fail_never=fail_never,
        model_required_attributes=default_map.get("model_required_attributes"),
        column_required_attributes=default_map.get("column_required_attributes"),
        log_level=log_level,
        enable_debug_logging=enable_debug_logging,
        enable_file_logging=enable_file_logging,
        log_file_path=log_file_path,
    )

    output = Output(config=config)

    rule_apply_enums = (
        [ValidationRuleSetEnum[name] for name in rule_apply]
        if rule_apply
        else DEFAULT_RULESETS
    )
    rule_ignore_enums = (
        [ValidationRuleSetEnum[name] for name in rule_ignore] if rule_ignore else []
    )

    rulesets = [rule for rule in rule_apply_enums if rule not in rule_ignore_enums]

    rb_validator = RuleSetBasedValidation(config, rulesets)

    # Call pre_validate_all on all validators
    rb_validator.pre_validate_all()

    # Validate all files
    for i, path in enumerate(file_paths, 1):
        validation_output = rb_validator.validate_file(path)
        output.print_validation_output(validation_output)

    # Determine exit code based on validation results
    exit_code = 1 if output.summary.invalid_file_count > 0 else 0
    if config.fail_mode == FailModeEnum.NEVER:
        exit_code = 0

    # Call post_validate_all with exit code
    rb_validator.post_validate_all(exit_code)

    # End control (this will handle the actual exit behavior)
    output.end_control()


if __name__ == "__main__":
    main()  # pragma: no cover
