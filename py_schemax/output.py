import json
from enum import Enum

import click

from py_schemax.schema.validation import ValidationOutputSchema
from py_schemax.summary import Summary


class OutputFormatEnum(Enum):
    JSON = "json"
    TEXT = "text"


class OutputLevelEnum(Enum):
    SILENT = 0
    VERBOSE = 1
    QUIET = 2


class FailModeEnum(Enum):
    FAIL_FAST = 0
    FAIL_NEVER = 1
    FAIL_AFTER = 2


class OutputControl:
    def __init__(self, summary: Summary | None = None) -> None:
        self.output_format = OutputFormatEnum.TEXT
        self.output_level = OutputLevelEnum.QUIET
        self.fail_mode = FailModeEnum.FAIL_AFTER
        self.show_summary = True

        self.summary = summary or Summary()

    def set_from_inputs(
        self,
        output_format: str | None = None,
        use_json: bool | None = None,
        quiet: bool | None = None,
        verbose: bool | None = None,
        silent: bool | None = None,
        fail_fast: bool | None = None,
        fail_never: bool | None = None,
        fail_after: bool | None = None,
    ) -> None:
        # set defaults
        output_format = output_format or "text"
        use_json = use_json or False
        quiet = quiet or True
        verbose = verbose or False
        silent = silent or False
        fail_fast = fail_fast or False
        fail_never = fail_never or False
        fail_after = fail_after or True

        # Set output format based on flags
        if use_json:
            self.output_format = OutputFormatEnum.JSON
        else:
            self.output_format = OutputFormatEnum(output_format)

        # Set output level based on flags (in priority order)
        if silent:
            self.output_level = OutputLevelEnum.SILENT
        elif verbose:
            self.output_level = OutputLevelEnum.VERBOSE
        elif quiet:
            self.output_level = OutputLevelEnum.QUIET

        # Set fail mode based on flags (in priority order)
        if fail_fast:
            self.fail_mode = FailModeEnum.FAIL_FAST
        elif fail_never:
            self.fail_mode = FailModeEnum.FAIL_NEVER
        else:
            self.fail_mode = FailModeEnum.FAIL_AFTER

    def __print_formatted_validation_output(
        self, validation_output: ValidationOutputSchema
    ) -> None:
        """Print validation output based on the output format and level."""
        if self.output_format == OutputFormatEnum.JSON:
            click.echo(json.dumps(validation_output))
        else:
            if not validation_output["valid"]:
                click.secho(f"❌ {validation_output['file_path']}", fg="red")
                for err in validation_output["errors"]:
                    click.secho(
                        f"    - {err['error_at']} : {err['message']}", fg="bright_black"
                    )
            else:
                click.secho(f"✅ {validation_output['file_path']}", fg="green")

    def print_validation_output(
        self, validation_output: ValidationOutputSchema
    ) -> None:
        """Print validation output based on the output format and level."""
        if not validation_output["valid"]:
            self.summary.add_record(
                valid=False, file_path=validation_output["file_path"]
            )
            if self.output_level in (OutputLevelEnum.QUIET, OutputLevelEnum.VERBOSE):
                self.__print_formatted_validation_output(validation_output)
            if self.fail_mode == FailModeEnum.FAIL_FAST:
                self.end_control()
        else:
            self.summary.add_record(
                valid=True, file_path=validation_output["file_path"]
            )
            if self.output_level == OutputLevelEnum.VERBOSE:
                self.__print_formatted_validation_output(validation_output)

    def end_control(self) -> None:
        if self.summary.invalid_file_count > 0:
            if self.fail_mode in (FailModeEnum.FAIL_AFTER, FailModeEnum.FAIL_FAST):
                raise click.ClickException("Validation completed with errors!")
            else:
                click.echo("Validation completed with errors!", err=True)
        else:
            click.echo("Validation completed successfully!", err=True)
