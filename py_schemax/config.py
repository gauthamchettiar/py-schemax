from enum import Enum


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


class Config:
    """Configuration manager for py-schemax CLI options."""

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        self.reset()

    def reset(self) -> None:
        """Reset all configuration to default values."""
        self.__output_format = OutputFormatEnum.TEXT
        self.__output_level = OutputLevelEnum.QUIET
        self.__fail_mode = FailModeEnum.FAIL_AFTER
        self.__no_cache_read = False
        self.__no_cache_write = False

    def set_output_format(
        self, output_format: str | None = None, use_json: bool | None = None
    ) -> None:
        """Set the output format based on CLI flags."""
        output_format = output_format or "text"
        use_json = use_json or False

        # Set output format based on flags
        if use_json:
            self.__output_format = OutputFormatEnum.JSON
        else:
            self.__output_format = OutputFormatEnum(output_format)

    def set_output_level(
        self,
        quiet: bool | None = None,
        verbose: bool | None = None,
        silent: bool | None = None,
    ) -> None:
        """Set the output level based on CLI flags (in priority order)."""
        quiet = quiet or True
        verbose = verbose or False
        silent = silent or False

        # Set output level based on flags (in priority order)
        if silent:
            self.__output_level = OutputLevelEnum.SILENT
        elif verbose:
            self.__output_level = OutputLevelEnum.VERBOSE
        elif quiet:
            self.__output_level = OutputLevelEnum.QUIET

    def set_fail_mode(
        self,
        fail_after: bool | None = None,
        fail_fast: bool | None = None,
        fail_never: bool | None = None,
    ) -> None:
        """Set the failure mode based on CLI flags."""
        fail_after = fail_after or True
        fail_fast = fail_fast or False
        fail_never = fail_never or False

        if fail_fast:
            self.__fail_mode = FailModeEnum.FAIL_FAST
        elif fail_never:
            self.__fail_mode = FailModeEnum.FAIL_NEVER
        else:
            self.__fail_mode = FailModeEnum.FAIL_AFTER

    def set_cache(
        self,
        no_cache_read: bool | None = None,
        no_cache_write: bool | None = None,
        no_cache: bool | None = None,
    ) -> None:
        """Set cache flags to disable reading or writing."""
        self.__no_cache_read = no_cache or no_cache_read or False
        self.__no_cache_write = no_cache or no_cache_write or False

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
    def no_cache_read(self) -> bool:
        """Get the current no_cache_read flag."""
        return self.__no_cache_read

    @property
    def no_cache_write(self) -> bool:
        """Get the current no_cache_write flag."""
        return self.__no_cache_write
