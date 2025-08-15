"""Main CLI module for py-schemax."""

from typing import List

import click

from py_schemax import __version__
from py_schemax.config import Config, OutputFormatEnum
from py_schemax.output import Output
from py_schemax.utils import accept_file_paths_as_stdin
from py_schemax.validator import validate_file


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
@click.option(
    "--no-cache-read",
    is_flag=True,
    default=False,
    help="Disable reading from the cache",
)
@click.option(
    "--no-cache-write",
    is_flag=True,
    default=False,
    help="Disable writing to the cache",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable all caching",
)
@click.option(
    "--cache_dir",
    default=".schemax_cache/validation.pickle",
    help="Directory to store cache files",
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
    no_cache_read: bool,
    no_cache_write: bool,
    no_cache: bool,
    cache_dir: str,
) -> None:
    """Validate a file against the Defined Schema.

    FILE_PATHS: One or More Paths to JSON or YAML file to validate.
    """
    file_paths = accept_file_paths_as_stdin(file_paths)

    config = Config()
    config.set_output_format(output_format=output_format, use_json=use_json)
    config.set_output_level(quiet=quiet, verbose=verbose, silent=silent)
    config.set_fail_mode(
        fail_fast=fail_fast, fail_never=fail_never, fail_after=fail_after
    )
    config.set_cache(
        no_cache_read=no_cache_read, no_cache_write=no_cache_write, no_cache=no_cache
    )

    output = Output(config=config)

    for path in file_paths:
        validation_output = validate_file(config, path)
        output.print_validation_output(validation_output)

    output.end_control()


if __name__ == "__main__":
    main()  # pragma: no cover
