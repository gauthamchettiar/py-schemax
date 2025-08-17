import os
import tomllib
from configparser import ConfigParser, ParsingError
from enum import Enum
from fileinput import filename
from pathlib import Path
from typing import Any, List, Tuple


class OutputFormatEnum(Enum):
    JSON = "json"
    TEXT = "text"


class OutputLevelEnum(Enum):
    SILENT = "silent"
    VERBOSE = "verbose"
    QUIET = "quiet"


class FailModeEnum(Enum):
    FAST = "fast"
    NEVER = "never"
    AFTER = "after"


DEFAULT_CONFIG_FILES = ["schemax.ini", "schemax.toml", "pyproject.toml"]


class DefaultConfig:
    """Default configuration values for py-schemax."""

    output_format = OutputFormatEnum.TEXT
    output_level = OutputLevelEnum.QUIET
    fail_mode = FailModeEnum.AFTER


class Config:
    """Configuration manager for py-schemax CLI options."""

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        self.reset()

    def reset(self) -> None:
        """Reset all configuration to default values."""
        self.__output_format = DefaultConfig.output_format
        self.__output_level = DefaultConfig.output_level
        self.__fail_mode = DefaultConfig.fail_mode

    def set_output_format(
        self, output_format: str | None = None, use_json: bool | None = None
    ) -> None:
        """Set the output format based on CLI flags."""
        # Set output format based on flags
        if use_json:
            self.__output_format = OutputFormatEnum.JSON
        elif output_format:
            self.__output_format = OutputFormatEnum(output_format)
        else:
            self.__output_format = DefaultConfig.output_format

    def set_output_level(
        self,
        output_level: str | None = None,
        output_level_verbose: bool | None = None,
        output_level_silent: bool | None = None,
    ) -> None:
        """Set the output level based on CLI flags (in priority order)."""
        if output_level_silent:
            self.__output_level = OutputLevelEnum.SILENT
        elif output_level_verbose:
            self.__output_level = OutputLevelEnum.VERBOSE
        elif output_level:
            self.__output_level = OutputLevelEnum(output_level)
        else:
            self.__output_level = DefaultConfig.output_level

    def set_fail_mode(
        self,
        fail_mode: str | None = None,
        fail_fast: bool | None = None,
        fail_never: bool | None = None,
    ) -> None:
        """Set the failure mode based on CLI flags."""
        if fail_fast:
            self.__fail_mode = FailModeEnum.FAST
        elif fail_never:
            self.__fail_mode = FailModeEnum.NEVER
        elif fail_mode:
            self.__fail_mode = FailModeEnum(fail_mode)
        else:
            self.__fail_mode = DefaultConfig.fail_mode

    @property
    def output_format(self) -> OutputFormatEnum:
        """Get the current output format."""
        return self.__output_format

    @property
    def output_level(self) -> OutputLevelEnum:
        """Get the current output level."""
        return self.__output_level

    @property
    def fail_mode(self) -> FailModeEnum:
        """Get the current failure mode."""
        return self.__fail_mode


def parse_config_files(
    file_paths: List[str], section_name: str
) -> Tuple[str, dict[str, Any]]:
    parsed_configs = {}
    for str_file_path in file_paths:
        file_path = Path(str_file_path)
        if file_path.suffix == ".ini":
            parsed_configs = parse_ini_config_file(
                str_file_path, f"schemax.{section_name}"
            )
        elif file_path.suffix == ".toml":
            parsed_configs = parse_toml_config_file(
                str_file_path, f"schemax.{section_name}"
            ) or parse_toml_config_file(str_file_path, f"tool.schemax.{section_name}")
        if parsed_configs:
            parsed_configs = {
                k: v.strip('"') if isinstance(v, str) else v
                for k, v in parsed_configs.items()
            }
            return str_file_path, parsed_configs

    return "", parsed_configs


def parse_ini_config_file(ini_file_path: str, section_name: str) -> dict[str, Any]:
    cfg_parser = ConfigParser()
    try:
        cfg_parser.read(ini_file_path)
    except ParsingError as e:
        return {}

    if section_name not in cfg_parser:
        return {}

    return dict(cfg_parser[section_name])


def parse_toml_config_file(toml_file_path: str, section_name: str) -> dict[str, Any]:
    try:
        with open(toml_file_path, "rb") as f:
            toml_parser = tomllib.load(f)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return {}

    for sec in section_name.split("."):
        toml_parser = toml_parser.get(sec, {})

    return toml_parser
