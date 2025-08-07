from py_schemax.output import (
    FailModeEnum,
    OutputControl,
    OutputFormatEnum,
    OutputLevelEnum,
)


def test_default_flags():
    output_control = OutputControl()
    assert output_control.output_format == OutputFormatEnum.TEXT
    assert output_control.output_level == OutputLevelEnum.QUIET
    assert output_control.fail_mode == FailModeEnum.FAIL_AFTER
    assert output_control.show_summary

    output_control.set_from_inputs()

    assert output_control.output_format == OutputFormatEnum.TEXT
    assert output_control.output_level == OutputLevelEnum.QUIET
    assert output_control.fail_mode == FailModeEnum.FAIL_AFTER
    assert output_control.show_summary


def test_calculated_flags():
    output_control = OutputControl()

    # Test setting output format
    output_control.set_from_inputs(output_format="json")
    assert output_control.output_format == OutputFormatEnum.JSON
    output_control.set_from_inputs(output_format="text", use_json=True)
    assert output_control.output_format == OutputFormatEnum.JSON

    # Test setting output level
    output_control.set_from_inputs(quiet=True)
    assert output_control.output_level == OutputLevelEnum.QUIET
    output_control.set_from_inputs(verbose=True)
    assert output_control.output_level == OutputLevelEnum.VERBOSE
    output_control.set_from_inputs(silent=True)
    assert output_control.output_level == OutputLevelEnum.SILENT
    output_control.set_from_inputs(quiet=True, verbose=True)
    assert output_control.output_level == OutputLevelEnum.VERBOSE
    output_control.set_from_inputs(quiet=True, verbose=True, silent=True)
    assert output_control.output_level == OutputLevelEnum.SILENT

    # Test setting fail mode
    output_control.set_from_inputs(fail_fast=True)
    assert output_control.fail_mode == FailModeEnum.FAIL_FAST
    output_control.set_from_inputs(fail_never=True)
    assert output_control.fail_mode == FailModeEnum.FAIL_NEVER
    output_control.set_from_inputs(fail_after=True)
    assert output_control.fail_mode == FailModeEnum.FAIL_AFTER
    output_control.set_from_inputs(fail_fast=True, fail_never=True)
    assert output_control.fail_mode == FailModeEnum.FAIL_FAST
    output_control.set_from_inputs(fail_fast=True, fail_never=True, fail_after=True)
    assert output_control.fail_mode == FailModeEnum.FAIL_FAST

    # Test Summary flags
    output_control.set_from_inputs(show_summary=True)
    assert output_control.show_summary
    output_control.set_from_inputs(no_summary=True)
    assert not output_control.show_summary
    output_control.set_from_inputs(no_summary=True, show_summary=True)
    assert not output_control.show_summary
    output_control.set_from_inputs(quiet=True)
    assert output_control.show_summary
    output_control.set_from_inputs(verbose=True)
    assert output_control.show_summary
    output_control.set_from_inputs(silent=True)
    assert not output_control.show_summary
    output_control.set_from_inputs(silent=True, show_summary=True)
    assert output_control.show_summary
    output_control.set_from_inputs(silent=True, no_summary=True)
    assert not output_control.show_summary
