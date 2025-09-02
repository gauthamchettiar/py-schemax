import sys
import tomllib
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from loguru import logger

if TYPE_CHECKING:
    from py_schemax.rulesets import ValidationRuleSetEnum


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
            log_file_path: Path to log file (enables file logging when provided)
            log_file_rotation: When to rotate log files
            log_file_retention: How long to keep old log files
            enable_console_logging: Whether to enable console logging
            console_format: Custom format for console output
            file_format: Custom format for file output
        """
        self.level = level.value if isinstance(level, LogLevelEnum) else level
        self.log_file_path = Path(log_file_path) if log_file_path else None
        self.log_file_rotation = log_file_rotation
        self.log_file_retention = log_file_retention
        self.enable_console_logging = enable_console_logging

        # Default formats
        self.console_format = console_format or (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[name]}</cyan> | "
            "<level>{message}</level>"
        )

        self.file_format = file_format or (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[name]} | {message}"
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

        # Add file handler if log file path is provided
        if self.log_file_path:
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


class DefaultConfig:
    """Default configuration values for py-schemax."""

    output_format = OutputFormatEnum.TEXT
    output_level = OutputLevelEnum.QUIET
    fail_mode = FailModeEnum.AFTER
    log_level = LogLevelEnum.INFO
    log_file_path = None
    rulesets = ("RV_SCHEMA",)
    config_files = ("schemax.toml", "pyproject.toml")


class Config:
    """Configuration manager for py-schemax CLI options with fluent API."""

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        self.reset()

    def reset(self) -> "Config":
        """Reset all configuration to default values."""
        self.__output_format = DefaultConfig.output_format
        self.__output_level = DefaultConfig.output_level
        self.__fail_mode = DefaultConfig.fail_mode
        self.__enforce_model_required_attributes: list[str] = []
        self.__enforce_column_required_attributes: dict[str, list[str]] = {}
        self.__log_level = DefaultConfig.log_level
        self.__log_file_path: str | None = DefaultConfig.log_file_path
        self.__logging = LogConfig(
            level=self.__log_level,
            log_file_path=self.__log_file_path,
        )
        self.__logging.setup_logging()
        return self

    def set_output_format(
        self,
        output_format: str | OutputFormatEnum | None = None,
        use_json: bool | None = None,
    ) -> "Config":
        """Set the output format based on CLI flags.

        Args:
            output_format: Output format as string or enum
            use_json: Flag to force JSON output

        Returns:
            Self for method chaining
        """
        if use_json:
            self.__output_format = OutputFormatEnum.JSON
        elif output_format:
            if isinstance(output_format, str):
                self.__output_format = OutputFormatEnum(output_format)
            else:
                self.__output_format = output_format
        else:
            self.__output_format = DefaultConfig.output_format
        return self

    def set_output_level(
        self,
        output_level: str | OutputLevelEnum | None = None,
        output_level_verbose: bool | None = None,
        output_level_silent: bool | None = None,
    ) -> "Config":
        """Set the output level based on CLI flags (in priority order).

        Args:
            output_level: Output level as string or enum
            output_level_verbose: Flag for verbose output
            output_level_silent: Flag for silent output

        Returns:
            Self for method chaining
        """
        if output_level_silent:
            self.__output_level = OutputLevelEnum.SILENT
        elif output_level_verbose:
            self.__output_level = OutputLevelEnum.VERBOSE
        elif output_level:
            if isinstance(output_level, str):
                self.__output_level = OutputLevelEnum(output_level)
            else:
                self.__output_level = output_level
        else:
            self.__output_level = DefaultConfig.output_level
        return self

    def set_fail_mode(
        self,
        fail_mode: str | FailModeEnum | None = None,
        fail_fast: bool | None = None,
        fail_never: bool | None = None,
    ) -> "Config":
        """Set the failure mode based on CLI flags.

        Args:
            fail_mode: Fail mode as string or enum
            fail_fast: Flag for fail-fast behavior
            fail_never: Flag for never-fail behavior

        Returns:
            Self for method chaining
        """
        if fail_fast:
            self.__fail_mode = FailModeEnum.FAST
        elif fail_never:
            self.__fail_mode = FailModeEnum.NEVER
        elif fail_mode:
            if isinstance(fail_mode, str):
                self.__fail_mode = FailModeEnum(fail_mode)
            else:
                self.__fail_mode = fail_mode
        else:
            self.__fail_mode = DefaultConfig.fail_mode
        return self

    def set_required_attributes(
        self,
        model_required_attributes: list[str] | None = None,
        column_required_attributes: dict[str, list[str]] | None = None,
    ) -> "Config":
        """Set the required attributes.

        Args:
            model_required_attributes: List of required model attributes
            column_required_attributes: Dict of required column attributes by type

        Returns:
            Self for method chaining
        """
        if model_required_attributes is not None:
            self.__enforce_model_required_attributes = model_required_attributes
        if column_required_attributes is not None:
            self.__enforce_column_required_attributes = column_required_attributes
        return self

    def set_logging(
        self,
        log_level: str | LogLevelEnum | None = None,
        log_file_path: str | None = None,
        enable_debug_logging: bool | None = None,
    ) -> "Config":
        """Set logging configuration based on CLI flags.

        Args:
            log_level: Log level as string or enum
            log_file_path: Path to log file (enables file logging automatically)
            enable_debug_logging: Flag to enable debug logging

        Returns:
            Self for method chaining
        """
        if enable_debug_logging:
            self.__log_level = LogLevelEnum.DEBUG
        elif log_level:
            if isinstance(log_level, str):
                self.__log_level = LogLevelEnum(log_level)
            else:
                self.__log_level = log_level
        else:
            self.__log_level = DefaultConfig.log_level

        self.__log_file_path = log_file_path or DefaultConfig.log_file_path

        self.__logging = LogConfig(
            level=self.__log_level,
            log_file_path=self.__log_file_path,
        )
        self.__logging.setup_logging()
        return self

    def set_rulesets(
        self,
        rule_apply: tuple[str, ...] | None = None,
        rule_ignore: tuple[str, ...] | None = None,
    ) -> "Config":
        """Set the rulesets for validation.

        Args:
            rule_apply: Tuple of rules to apply
            rule_exclude: Tuple of rules to exclude

        Returns:
            Self for method chaining
        """
        from py_schemax.rulesets import ValidationRuleSetEnum

        self.__rulesets = tuple(
            ValidationRuleSetEnum[rule]
            for rule in rule_apply or DefaultConfig.rulesets
            if rule not in (rule_ignore or ())
        )
        return self

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
    def log_file_path(self) -> str | None:
        """Get the log file path."""
        return self.__log_file_path

    @property
    def logging(self) -> LogConfig:
        """Get the logging configuration."""
        return self.__logging

    @property
    def rulesets(self) -> tuple["ValidationRuleSetEnum", ...]:
        """Get the current rulesets."""
        return self.__rulesets

    def as_dict(self) -> dict[str, Any]:
        return {
            "output_format": self.output_format.value,
            "output_level": self.output_level.value,
            "fail_mode": self.fail_mode.value,
            "model_required_attributes": self.model_required_attributes,
            "column_required_attributes": self.column_required_attributes,
            "log_level": self.log_level.value,
            "log_file_path": self.log_file_path,
        }


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
