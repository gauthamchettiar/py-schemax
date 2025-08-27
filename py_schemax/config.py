import tomllib
from enum import Enum
from pathlib import Path
from typing import Any, List, Tuple, TypedDict, Unpack


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


DEFAULT_CONFIG_FILES = ["schemax.toml", "pyproject.toml"]


class _OutputFormatKwargs(TypedDict, total=False):
    """Type hints for output format configuration parameters."""

    output_format: str | None
    use_json: bool | None


class _OutputLevelKwargs(TypedDict, total=False):
    """Type hints for output level configuration parameters."""

    output_level: str | None
    output_level_verbose: bool | None
    output_level_silent: bool | None


class _FailModeKwargs(TypedDict, total=False):
    """Type hints for fail mode configuration parameters."""

    fail_mode: str | None
    fail_fast: bool | None
    fail_never: bool | None


class _RequiredAttributesKwargs(TypedDict, total=False):
    """Type hints for required attributes configuration parameters."""

    model_required_attributes: list[str] | None
    column_required_attributes: dict[str, list[str]] | None


class _ConfigKwargs(
    _OutputFormatKwargs, _OutputLevelKwargs, _FailModeKwargs, _RequiredAttributesKwargs
):
    """Complete type hints for all configuration parameters."""

    pass


class DefaultConfig:
    """Default configuration values for py-schemax."""

    output_format = OutputFormatEnum.TEXT
    output_level = OutputLevelEnum.QUIET
    fail_mode = FailModeEnum.AFTER


class Config:
    """Configuration manager for py-schemax CLI options."""

    def __init__(self, **kwargs: Unpack[_ConfigKwargs]) -> None:
        """Initialize configuration with provided values or defaults.

        Args:
            **kwargs: Configuration parameters. See ConfigKwargs for supported options.
        """
        self._set_all_config(**kwargs)

    def reset(self) -> None:
        """Reset all configuration to default values."""
        self._set_all_config()

    def _set_all_config(self, **kwargs: Unpack[_ConfigKwargs]) -> None:
        """Set all configuration options from keyword arguments."""
        # Extract parameters for each setter using type-safe approach
        output_format_params = {
            k: v for k, v in kwargs.items() if k in _OutputFormatKwargs.__annotations__
        }
        output_level_params = {
            k: v for k, v in kwargs.items() if k in _OutputLevelKwargs.__annotations__
        }
        fail_mode_params = {
            k: v for k, v in kwargs.items() if k in _FailModeKwargs.__annotations__
        }

        self.set_output_format(**output_format_params)  # type: ignore[arg-type]
        self.set_output_level(**output_level_params)  # type: ignore[arg-type]
        self.set_fail_mode(**fail_mode_params)  # type: ignore[arg-type]
        self.set_required_attributes(
            kwargs.get("model_required_attributes") or [],
            kwargs.get("column_required_attributes") or {},
        )

    def set_output_format(self, **kwargs: Unpack[_OutputFormatKwargs]) -> None:
        """Set the output format based on CLI flags."""
        output_format = kwargs.get("output_format")
        use_json = kwargs.get("use_json")

        # Set output format based on flags
        if use_json:
            self.__output_format = OutputFormatEnum.JSON
        elif output_format:
            self.__output_format = OutputFormatEnum(output_format)
        else:
            self.__output_format = DefaultConfig.output_format

    def set_output_level(self, **kwargs: Unpack[_OutputLevelKwargs]) -> None:
        """Set the output level based on CLI flags (in priority order)."""
        output_level = kwargs.get("output_level")
        output_level_verbose = kwargs.get("output_level_verbose")
        output_level_silent = kwargs.get("output_level_silent")

        if output_level_silent:
            self.__output_level = OutputLevelEnum.SILENT
        elif output_level_verbose:
            self.__output_level = OutputLevelEnum.VERBOSE
        elif output_level:
            self.__output_level = OutputLevelEnum(output_level)
        else:
            self.__output_level = DefaultConfig.output_level

    def set_fail_mode(self, **kwargs: Unpack[_FailModeKwargs]) -> None:
        """Set the failure mode based on CLI flags."""
        fail_mode = kwargs.get("fail_mode")
        fail_fast = kwargs.get("fail_fast")
        fail_never = kwargs.get("fail_never")

        if fail_fast:
            self.__fail_mode = FailModeEnum.FAST
        elif fail_never:
            self.__fail_mode = FailModeEnum.NEVER
        elif fail_mode:
            self.__fail_mode = FailModeEnum(fail_mode)
        else:
            self.__fail_mode = DefaultConfig.fail_mode

    def set_required_attributes(
        self,
        model_required_attributes: list[str],
        column_required_attributes: dict[str, list[str]],
    ) -> None:
        """Set the required attributes."""
        self.__enforce_model_required_attributes = model_required_attributes
        self.__enforce_column_required_attributes = column_required_attributes

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

    @property
    def model_required_attributes(self) -> list[str]:
        """Get the list of required attributes."""
        return self.__enforce_model_required_attributes

    @property
    def column_required_attributes(self) -> dict[str, list[str]]:
        """Get the list of required column attributes."""
        return self.__enforce_column_required_attributes


def parse_config_files(
    file_paths: List[str], section_name: str
) -> Tuple[str, dict[str, Any]]:
    parsed_configs = {}
    for str_file_path in file_paths:
        file_path = Path(str_file_path)
        if file_path.suffix == ".toml":
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


def parse_toml_config_file(toml_file_path: str, section_name: str) -> dict[str, Any]:
    try:
        with open(toml_file_path, "rb") as f:
            toml_parser = tomllib.load(f)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return {}

    for sec in section_name.split("."):
        toml_parser = toml_parser.get(sec, {})

    return toml_parser
