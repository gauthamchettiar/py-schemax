import json

import click
from click.exceptions import Exit

from py_schemax.config import Config, FailModeEnum, OutputFormatEnum, OutputLevelEnum
from py_schemax.summary import Summary
from py_schemax.validator import ValidationOutputSchema


class Output:
    def __init__(
        self, config: Config | None = None, summary: Summary | None = None
    ) -> None:
        self.__config = config or Config()
        self.__summary = summary or Summary()
        self.__logger = self.__config.logging.get_logger("schemax")

    def __print_formatted_validation_output(
        self, validation_output: ValidationOutputSchema
    ) -> None:
        """Print validation output based on the output format and level."""
        if self.__config.output_format == OutputFormatEnum.JSON:
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
        file_path = validation_output["file_path"]

        if not validation_output["valid"]:
            self.__summary.add_record(valid=False, file_path=file_path)
            if self.__config.output_level in (
                OutputLevelEnum.QUIET,
                OutputLevelEnum.VERBOSE,
            ):
                self.__print_formatted_validation_output(validation_output)
            if self.__config.fail_mode == FailModeEnum.FAST:
                self.end_control()
        else:
            self.__summary.add_record(valid=True, file_path=file_path)
            if self.__config.output_level == OutputLevelEnum.VERBOSE:
                self.__print_formatted_validation_output(validation_output)

    def end_control(self) -> None:
        if self.__summary.invalid_file_count > 0:
            if self.__config.fail_mode in (
                FailModeEnum.AFTER,
                FailModeEnum.FAST,
            ):
                self.__logger.error("Validation completed with errors!")
                raise Exit(1)
            else:
                self.__logger.warning("Validation completed with errors!")
        else:
            self.__logger.info("Validation completed successfully!")

    @property
    def summary(self) -> Summary:
        return self.__summary
