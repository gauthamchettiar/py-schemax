import sys
import tomllib
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional, Tuple, TypedDict, Unpack

from loguru import logger


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


class LogLevelEnum(Enum):
    """Available logging levels."""

    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogConfig:
    """Configuration for loguru logger."""

    def __init__(
        self,
        level: str | LogLevelEnum = LogLevelEnum.INFO,
        enable_file_logging: bool = False,
        log_file_path: Optional[str | Path] = None,
        log_file_rotation: str = "10 MB",
        log_file_retention: str = "10 days",
        enable_console_logging: bool = True,
        console_format: Optional[str] = None,
        file_format: Optional[str] = None,
    ):
        """Initialize logging configuration.

        Args:
            level: Logging level (INFO, DEBUG, etc.)
            enable_file_logging: Whether to enable file logging
            log_file_path: Path to log file (defaults to schemax.log)
            log_file_rotation: When to rotate log files
            log_file_retention: How long to keep old log files
            enable_console_logging: Whether to enable console logging
            console_format: Custom format for console output
            file_format: Custom format for file output
        """
        self.level = level.value if isinstance(level, LogLevelEnum) else level
        self.enable_file_logging = enable_file_logging
        self.log_file_path = (
            Path(log_file_path) if log_file_path else Path("schemax.log")
        )
        self.log_file_rotation = log_file_rotation
        self.log_file_retention = log_file_retention
        self.enable_console_logging = enable_console_logging

        # Default formats
        self.console_format = console_format or (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan> | "
            "<level>{message}</level>"
        )

        self.file_format = file_format or (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}"
        )

    def setup_logging(self) -> None:
        """Set up loguru logger with the given configuration.

        Args:
            config: LogConfig instance with logging settings
        """
        # Remove default logger
        logger.remove()

        # Add console handler if enabled
        if self.enable_console_logging:
            logger.add(
                sys.stderr,
                format=self.console_format,
                level=self.level,
                colorize=True,
            )

        # Add file handler if enabled
        if self.enable_file_logging:
            logger.add(
                self.log_file_path,
                format=self.file_format,
                level=self.level,
                rotation=self.log_file_rotation,
                retention=self.log_file_retention,
                encoding="utf-8",
            )

    def get_logger(self, name: str = __name__) -> Any:
        """Get a logger instance for the given name.

        Args:
            name: Logger name (usually __name__)

        Returns:
            Configured logger instance
        """
        return logger.bind(name=name)


DEFAULT_CONFIG_FILES = ["schemax.toml", "pyproject.toml"]
DEFAULT_LOG_FILE = "schemax.log"


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


class _LoggingKwargs(TypedDict, total=False):
    """Type hints for logging configuration parameters."""

    log_level: str | None
    enable_file_logging: bool | None
    log_file_path: str | None
    enable_debug_logging: bool | None


class _ConfigKwargs(
    _OutputFormatKwargs,
    _OutputLevelKwargs,
    _FailModeKwargs,
    _RequiredAttributesKwargs,
    _LoggingKwargs,
):
    """Complete type hints for all configuration parameters."""

    pass


class DefaultConfig:
    """Default configuration values for py-schemax."""

    output_format = OutputFormatEnum.TEXT
    output_level = OutputLevelEnum.QUIET
    fail_mode = FailModeEnum.AFTER
    log_level = LogLevelEnum.INFO
    enable_file_logging = False
    log_file_path = DEFAULT_LOG_FILE


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
        required_attributes_params = {
            k: v
            for k, v in kwargs.items()
            if k in _RequiredAttributesKwargs.__annotations__
        }
        logging_params = {
            k: v for k, v in kwargs.items() if k in _LoggingKwargs.__annotations__
        }

        self.set_output_format(**output_format_params)  # type: ignore[arg-type]
        self.set_output_level(**output_level_params)  # type: ignore[arg-type]
        self.set_fail_mode(**fail_mode_params)  # type: ignore[arg-type]
        self.set_required_attributes(**required_attributes_params)  # type: ignore[arg-type]
        self.set_logging(**logging_params)  # type: ignore[arg-type]

    def set_output_format(self, **kwargs: Unpack[_OutputFormatKwargs]) -> None:
        """Set the output format based on CLI flags."""
        output_format = kwargs.get("output_format") or DefaultConfig.output_format.value
        use_json = kwargs.get("use_json")

        # Set output format based on flags
        if use_json:
            self.__output_format = OutputFormatEnum.JSON
        else:
            self.__output_format = OutputFormatEnum(output_format)

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
        fail_mode = kwargs.get("fail_mode") or DefaultConfig.fail_mode.value
        fail_fast = kwargs.get("fail_fast")
        fail_never = kwargs.get("fail_never")

        if fail_fast:
            self.__fail_mode = FailModeEnum.FAST
        elif fail_never:
            self.__fail_mode = FailModeEnum.NEVER
        else:
            self.__fail_mode = FailModeEnum(fail_mode)

    def set_required_attributes(
        self, **kwargs: Unpack[_RequiredAttributesKwargs]
    ) -> None:
        """Set the required attributes."""
        self.__enforce_model_required_attributes = (
            kwargs.get("model_required_attributes") or []
        )
        self.__enforce_column_required_attributes = (
            kwargs.get("column_required_attributes") or {}
        )

    def set_logging(self, **kwargs: Unpack[_LoggingKwargs]) -> None:
        """Set logging configuration based on CLI flags."""
        log_level = kwargs.get("log_level") or DefaultConfig.log_level.value
        enable_file_logging = (
            kwargs.get("enable_file_logging") or DefaultConfig.enable_file_logging
        )
        log_file_path = kwargs.get("log_file_path") or DefaultConfig.log_file_path
        enable_debug_logging = kwargs.get("enable_debug_logging")

        if enable_debug_logging:
            self.__log_level = LogLevelEnum.DEBUG
        else:
            self.__log_level = LogLevelEnum(log_level)

        self.__enable_file_logging = enable_file_logging
        self.__log_file_path = log_file_path
        self.__logging = LogConfig(
            level=self.__log_level,
            enable_file_logging=self.__enable_file_logging,
            log_file_path=self.__log_file_path,
        )
        self.__logging.setup_logging()

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

    @property
    def log_level(self) -> LogLevelEnum:
        """Get the current log level."""
        return self.__log_level

    @property
    def enable_file_logging(self) -> bool:
        """Get whether file logging is enabled."""
        return self.__enable_file_logging

    @property
    def log_file_path(self) -> str:
        """Get the log file path."""
        return self.__log_file_path

    @property
    def logging(self) -> LogConfig:
        """Get the logging configuration."""
        return self.__logging


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
