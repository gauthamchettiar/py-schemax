import json

import click

from py_schemax.config import Config, FailModeEnum, OutputFormatEnum, OutputLevelEnum
from py_schemax.schema.validation import ValidationOutputSchema
from py_schemax.summary import Summary


class Output:
    def __init__(
        self, config: Config | None = None, summary: Summary | None = None
    ) -> None:
        self.config = config or Config()
        self.summary = summary or Summary()

    def __print_formatted_validation_output(
        self, validation_output: ValidationOutputSchema
    ) -> None:
        """Print validation output based on the output format and level."""
        if self.config.output_format == OutputFormatEnum.JSON:
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
            if self.config.output_level in (
                OutputLevelEnum.QUIET,
                OutputLevelEnum.VERBOSE,
            ):
                self.__print_formatted_validation_output(validation_output)
            if self.config.fail_mode == FailModeEnum.FAST:
                self.end_control()
        else:
            self.summary.add_record(
                valid=True, file_path=validation_output["file_path"]
            )
            if self.config.output_level == OutputLevelEnum.VERBOSE:
                self.__print_formatted_validation_output(validation_output)

    def end_control(self) -> None:
        if self.summary.invalid_file_count > 0:
            if self.config.fail_mode in (
                FailModeEnum.AFTER,
                FailModeEnum.FAST,
            ):
                raise click.ClickException("Validation completed with errors!")
            else:
                click.echo("Validation completed with errors!", err=True)
        else:
            click.echo("Validation completed successfully!", err=True)
