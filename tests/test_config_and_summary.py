from py_schemax.config import Config, FailModeEnum, OutputFormatEnum, OutputLevelEnum
from py_schemax.summary import Summary


class TestDefaultConfig:
    def test_default_values(self):
        config = Config()
        assert config.fail_mode == FailModeEnum.FAIL_AFTER
        assert config.output_format == OutputFormatEnum.TEXT
        assert config.output_level == OutputLevelEnum.QUIET

    def test_default_set_modes(self):
        config = Config()
        config.set_fail_mode()
        assert config.fail_mode == FailModeEnum.FAIL_AFTER

        config.set_output_format()
        assert config.output_format == OutputFormatEnum.TEXT

        config.set_output_level()
        assert config.output_level == OutputLevelEnum.QUIET


class TestSettingConfig:
    def test_set_fail_mode(self):
        config = Config()
        config.set_fail_mode(fail_fast=True)
        assert config.fail_mode == FailModeEnum.FAIL_FAST

        config.set_fail_mode(fail_never=True)
        assert config.fail_mode == FailModeEnum.FAIL_NEVER

        config.set_fail_mode(fail_after=True)
        assert config.fail_mode == FailModeEnum.FAIL_AFTER

        config.set_fail_mode(fail_fast=True, fail_never=True)
        assert config.fail_mode == FailModeEnum.FAIL_FAST

        config.set_fail_mode(fail_fast=True, fail_never=True, fail_after=True)
        assert config.fail_mode == FailModeEnum.FAIL_FAST

    def test_set_output_format(self):
        config = Config()
        config.set_output_format(use_json=True)
        assert config.output_format == OutputFormatEnum.JSON

        config.set_output_format(output_format="text")
        assert config.output_format == OutputFormatEnum.TEXT

        config.set_output_format(output_format="json")
        assert config.output_format == OutputFormatEnum.JSON

        config.set_output_format(output_format="text", use_json=True)
        assert config.output_format == OutputFormatEnum.JSON

    def test_set_output_level(self):
        config = Config()
        config.set_output_level(quiet=True)
        assert config.output_level == OutputLevelEnum.QUIET

        config.set_output_level(verbose=True)
        assert config.output_level == OutputLevelEnum.VERBOSE

        config.set_output_level(silent=True)
        assert config.output_level == OutputLevelEnum.SILENT

        config.set_output_level(quiet=True, verbose=True)
        assert config.output_level == OutputLevelEnum.VERBOSE

        config.set_output_level(quiet=True, verbose=True, silent=True)
        assert config.output_level == OutputLevelEnum.SILENT

    def test_reset(self):
        config = Config()
        config.reset()
        assert config.fail_mode == FailModeEnum.FAIL_AFTER
        assert config.output_format == OutputFormatEnum.TEXT
        assert config.output_level == OutputLevelEnum.QUIET

    from py_schemax.summary import Summary


class TestSummary:
    def test_add_summary_record(self):
        summary = Summary()
        summary.add_record(True, "file1.json")
        summary.add_record(False, "file2.json")
        summary.add_record(True, "file3.json")

        summary = summary.to_dict()
        assert summary["validated_file_count"] == 3
        assert summary["valid_file_count"] == 2
        assert summary["invalid_file_count"] == 1
        assert summary["error_files"] == ["file2.json"]
