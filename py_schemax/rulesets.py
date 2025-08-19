from enum import Enum
from pathlib import Path

from py_schemax.config import Config
from py_schemax.schema.validation import ValidationOutputSchema
from py_schemax.utils import merge_validation_outputs
from py_schemax.validator import FileValidator, PydanticSchemaValidator


class ValidationRuleSetEnum(Enum):
    PSX_VAL1 = PydanticSchemaValidator


DEFAULT_RULESETS = (ValidationRuleSetEnum.PSX_VAL1,)


def validate_file_by_ruleset(
    config: Config,
    file_path: str | Path,
    apply_rules: list[ValidationRuleSetEnum],
) -> ValidationOutputSchema:
    """Validate a file using the appropriate validator based on its extension."""
    file_validator = FileValidator(config)
    if (file_validator_output := file_validator.validate(file_path)).get(
        "valid", False
    ) is False:
        return file_validator_output
    previous_validated_content = file_validator.validated_content
    for rule in apply_rules:
        validator = rule.value(config)
        if (
            validator_output := validator.validate(previous_validated_content or {})
        ).get("valid", False) is False:
            return merge_validation_outputs(file_validator_output, validator_output)
        previous_validated_content = validator.validated_content

    return file_validator_output
