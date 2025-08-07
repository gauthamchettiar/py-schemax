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
        no_summary: bool | None = None,
        show_summary: bool | None = None,
    ):
        # set defaults
        output_format = output_format or "text"
        use_json = use_json or False
        quiet = quiet or True
        verbose = verbose or False
        silent = silent or False
        fail_fast = fail_fast or False
        fail_never = fail_never or False
        fail_after = fail_after or True
        no_summary = no_summary or False

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

        # Set summary display options
        if no_summary or (
            show_summary is None and self.output_level == OutputLevelEnum.SILENT
        ):
            self.show_summary = False
        elif show_summary is True:
            self.show_summary = True
        elif show_summary is None and self.output_level in (
            OutputLevelEnum.QUIET,
            OutputLevelEnum.VERBOSE,
        ):
            self.show_summary = True
        else:
            self.show_summary = False

    def __print_formatted_validation_output(
        self, validation_output: ValidationOutputSchema
    ):
        """Print validation output based on the output format and level."""
        if self.output_format == OutputFormatEnum.JSON:
            click.echo(json.dumps(validation_output))
        else:
            if not validation_output["valid"]:
                click.secho(f"❌ {validation_output['file_path']}", fg="red")
                for i, err in enumerate(validation_output["errors"], 1):
                    click.secho(
                        f"    - {err['error_at']} : {err['message']}", fg="bright_black"
                    )
            else:
                click.secho(f"✅ {validation_output['file_path']}", fg="green")

    @classmethod
    def __box(cls, text: str) -> str:
        lines = text.splitlines()
        width = max(len(line) for line in lines)
        top = "┌" + "─" * (width + 2) + "─┐"
        bottom = "└" + "─" * (width + 2) + "─┘"
        body = ["│ " + line.ljust(width) + " │" for line in lines]
        return "\n".join([top] + body + [bottom])

    def __print_formatted_summary(self):
        """Print summary of validation results."""
        if self.output_format == OutputFormatEnum.JSON:
            click.echo(json.dumps(self.summary.to_dict()))
        else:
            click.echo(
                "\n\n"
                + self.__box(
                    f"✅ VALID   = [{self.summary.valid_file_count} / {self.summary.validated_file_count}] \n❌ INVALID = [{self.summary.invalid_file_count} / {self.summary.validated_file_count}]"
                )
                + "\n\n"
            )

    def print_validation_output(self, validation_output: ValidationOutputSchema):
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
            if (
                self.output_level == OutputLevelEnum.VERBOSE
                or self.output_format == OutputFormatEnum.JSON
            ):
                self.__print_formatted_validation_output(validation_output)

    def print_summary(self):
        """Print the summary of validation results."""
        if self.show_summary:
            self.__print_formatted_summary()

    def end_control(self):
        if self.summary.invalid_file_count > 0:
            if self.fail_mode in (FailModeEnum.FAIL_AFTER, FailModeEnum.FAIL_FAST):
                if self.show_summary:
                    self.print_summary()
                raise click.ClickException("Validation completed with errors!")
            elif (
                self.fail_mode == FailModeEnum.FAIL_NEVER
                and self.output_format == OutputFormatEnum.TEXT
                and (self.output_level != OutputLevelEnum.SILENT or self.show_summary)
            ):
                print("Validation completed with errors!")
        else:
            if self.output_format == OutputFormatEnum.TEXT and (
                self.output_level != OutputLevelEnum.SILENT or self.show_summary
            ):
                print("Validation completed successfully!")
