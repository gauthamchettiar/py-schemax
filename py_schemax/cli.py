"""Main CLI module for py-schemax."""

import os
from configparser import ConfigParser
from typing import Any, Callable, List, MutableMapping

import click

from py_schemax import __version__
from py_schemax.config import Config, OutputFormatEnum
from py_schemax.output import Output
from py_schemax.utils import accept_file_paths_as_stdin
from py_schemax.validator import validate_file


def parse_config_file_for(
    section_name: str,
) -> Callable[[click.Context, click.Parameter, str], None]:
    """Parse the config file for a specific command."""
    section_name = f"schemax.{section_name}"

    def _parse(ctx: click.Context, param: click.Parameter, filename: str) -> None:
        """Load configuration from file into Click's default_map."""
        if not filename:
            return  # pragma: no cover
        if not os.path.exists(filename):
            if filename == "schemax.ini":
                return
            raise click.BadParameter(f"Config file '{filename}' not found")

        cfg = ConfigParser()
        cfg.read(filename)

        defaults: MutableMapping[str, Any] = ctx.default_map or {}

        if section_name not in cfg:
            return

        # Initialize ctx.default_map if it was None
        if ctx.default_map is None:
            ctx.default_map = defaults

        # Add each config option as a default
        for config in cfg[section_name]:
            defaults.setdefault(config, {})

        defaults.update(cfg[section_name])

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
    default="schemax.ini",
    callback=parse_config_file_for("validate"),
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
    default=OutputFormatEnum.TEXT.value,
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
    "--quiet",
    "output_level_quiet",
    is_flag=True,
    help="Suppress all output except errors",
    envvar="SCHEMAX_VALIDATE_QUIET",
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
    "--fail-after",
    is_flag=True,
    help="Exit with error code if any files are invalid at the end",
    envvar="SCHEMAX_VALIDATE_FAIL_AFTER",
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
def validate(
    file_paths: List[str],
    output_format: str,
    use_json: bool,
    output_level_quiet: bool,
    output_level_verbose: bool,
    output_level_silent: bool,
    fail_fast: bool,
    fail_never: bool,
    fail_after: bool,
) -> None:
    """Validate a file against the Defined Schema.

    FILE_PATHS: One or More Paths to JSON or YAML file to validate.
    """
    file_paths = accept_file_paths_as_stdin(file_paths)

    config = Config()
    config.set_output_format(output_format=output_format, use_json=use_json)
    config.set_output_level(
        quiet=output_level_quiet,
        verbose=output_level_verbose,
        silent=output_level_silent,
    )
    config.set_fail_mode(
        fail_fast=fail_fast, fail_never=fail_never, fail_after=fail_after
    )

    output = Output(config=config)

    for path in file_paths:
        validation_output = validate_file(config, path)
        output.print_validation_output(validation_output)

    output.end_control()


if __name__ == "__main__":
    main()  # pragma: no cover
