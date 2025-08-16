"""Main CLI module for py-schemax."""

import os
from configparser import ConfigParser
from typing import Any, Callable, List, MutableMapping

import click

from py_schemax import __version__
from py_schemax.config import (
    DEFAULT_CONFIG_FILES,
    Config,
    FailModeEnum,
    OutputFormatEnum,
    OutputLevelEnum,
    parse_config_files,
)
from py_schemax.output import Output
from py_schemax.utils import accept_file_paths_as_stdin
from py_schemax.validator import validate_file


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
        ctx.default_map = default_map

    return _parse


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """A powerful CLI tool for validating, managing, and maintaining data schema definitions using Pydantic models.

    Use --help to see available commands.
    """
    pass  # pragma: no cover


@main.command()
@click.argument("file_paths", nargs=-1, type=click.Path())
@click.option(
    "-c",
    "--config",
    type=click.Path(dir_okay=False),
    default=DEFAULT_CONFIG_FILES,
    multiple=True,
    callback=parse_config_files_for("validate"),
    is_eager=True,
    expose_value=False,
    help="Read option defaults from the specified INI file",
    show_default=True,
)
@click.option(
    "-o",
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
    envvar="SCHEMAX_VALIDATE_USE_JSON",
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
    envvar="SCHEMAX_VALIDATE_VERBOSE",
)
@click.option(
    "--silent",
    "output_level_silent",
    is_flag=True,
    help="Suppress all output, only exit with error codes, overrides --quiet and --verbose",
    envvar="SCHEMAX_VALIDATE_SILENT",
)
@click.option(
    "--fail-mode",
    type=click.Choice([e.value for e in FailModeEnum]),
    help="Failure mode for validation",
    envvar="SCHEMAX_VALIDATE_FAIL_MODE",
)
@click.option(
    "--fail-never",
    is_flag=True,
    help="Never exit with error code, useful for CI, overrides --fail-fast",
    envvar="SCHEMAX_VALIDATE_FAIL_NEVER",
)
@click.option(
    "--fail-fast",
    is_flag=True,
    help="Stop on first validation error, overrides --fail-never and --fail-after",
    envvar="SCHEMAX_VALIDATE_FAIL_FAST",
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
) -> None:
    """Validate a file against the Defined Schema.

    FILE_PATHS: One or More Paths to JSON or YAML file to validate.
    """
    file_paths = accept_file_paths_as_stdin(file_paths)
    config = Config()
    config.set_output_format(output_format=output_format, use_json=use_json)
    config.set_output_level(
        output_level=output_level,
        output_level_verbose=output_level_verbose,
        output_level_silent=output_level_silent,
    )
    config.set_fail_mode(
        fail_mode=fail_mode, fail_fast=fail_fast, fail_never=fail_never
    )

    output = Output(config=config)

    for path in file_paths:
        validation_output = validate_file(config, path)
        output.print_validation_output(validation_output)

    output.end_control()


if __name__ == "__main__":
    main()  # pragma: no cover
