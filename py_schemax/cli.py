"""Main CLI module for py-schemax."""

import os
from typing import List

import click

from py_schemax import __version__
from py_schemax.validator import Validator

from .output import OutputControl, OutputFormatEnum
from .utils import accept_file_paths_as_stdin, get_hash_of_file


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """A CLI tool for schema validation and management.

    This is the main entry point for the py-schemax CLI application.
    Use --help to see available commands.
    """
    os.makedirs(".schemax", exist_ok=True)


@main.command()
@click.argument("file_paths", nargs=-1, type=click.Path())
@click.option(
    "--out",
    "output_format",
    type=click.Choice([e.value for e in OutputFormatEnum]),
    default=OutputFormatEnum.TEXT.value,
    help="Output format for validation results",
)
@click.option(
    "--json",
    "use_json",
    is_flag=True,
    help="Output results in JSON format, overrides --out option",
)
@click.option(
    "--quiet",
    is_flag=True,
    default=True,
    help="Suppress all output except errors",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Show detailed validation progress with ok and errors, overrides --quiet",
)
@click.option(
    "--silent",
    is_flag=True,
    default=False,
    help="Suppress all output, only exit with error codes, overrides --quiet and --verbose",
)
@click.option(
    "--fail-after",
    is_flag=True,
    default=True,
    help="Exit with error code if any files are invalid at the end",
)
@click.option(
    "--fail-never",
    is_flag=True,
    default=False,
    help="Never exit with error code, useful for CI, overrides --fail-fast",
)
@click.option(
    "--fail-fast",
    is_flag=True,
    default=False,
    help="Stop on first validation error, overrides --fail-never and --fail-after",
)
def validate(
    file_paths: List[str],
    output_format: str,
    use_json: bool,
    quiet: bool,
    verbose: bool,
    silent: bool,
    fail_fast: bool,
    fail_never: bool,
    fail_after: bool,
) -> None:
    """Validate a file against the Defined Schema.

    FILE_PATHS: One or More Paths to JSON or YAML file to validate.
    """
    file_paths = accept_file_paths_as_stdin(file_paths)

    output_control = OutputControl()
    output_control.set_from_inputs(
        output_format=output_format,
        use_json=use_json,
        quiet=quiet,
        verbose=verbose,
        silent=silent,
        fail_fast=fail_fast,
        fail_never=fail_never,
        fail_after=fail_after,
    )

    validator = Validator()

    for path in file_paths:
        try:
            file_hash = get_hash_of_file(path)
        except FileNotFoundError:
            file_hash = None
        validation_output = validator.validate_schema_file(path, file_hash)
        output_control.print_validation_output(validation_output)

    output_control.end_control()


if __name__ == "__main__":
    main()
