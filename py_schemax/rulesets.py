from enum import Enum
from pathlib import Path

from py_schemax import config
from py_schemax.config import Config
from py_schemax.schema.validation import ValidationOutputSchema
from py_schemax.utils import merge_validation_outputs
from py_schemax.validator import (
    FileValidator,
    PydanticSchemaValidator,
    UniqueFQNValidator,
)


class ValidationRuleSetEnum(Enum):
    PSX_VAL1 = PydanticSchemaValidator
    PSX_VAL2 = UniqueFQNValidator


DEFAULT_RULESETS = (ValidationRuleSetEnum.PSX_VAL1, ValidationRuleSetEnum.PSX_VAL2)


class RuleSetBasedValidation:
    def __init__(
        self, config: Config, apply_rules: list[ValidationRuleSetEnum]
    ) -> None:
        self.__config = config
        self.__validators = [rule.value(config) for rule in apply_rules]

    def validate_file(self, file_path: str | Path) -> ValidationOutputSchema:
        file_validator = FileValidator(self.__config)
        if (file_validator_output := file_validator.validate(file_path)).get(
            "valid", False
        ) is False:
            return file_validator_output

        for validator in self.__validators:
            if (
                validator_output := validator.validate(
                    file_validator.validated_content or {}, str(file_path)
                )
            ).get("valid", False) is False:
                return merge_validation_outputs(file_validator_output, validator_output)

        return file_validator_output


# def validate_file_by_ruleset(
#     config: Config,
#     file_path: str | Path,
#     apply_rules: list[ValidationRuleSetEnum],
# ) -> ValidationOutputSchema:
#     """Validate a file using the appropriate validator based on its extension."""
#     file_validator = FileValidator(config)
#     if (file_validator_output := file_validator.validate(file_path)).get(
#         "valid", False
#     ) is False:
#         return file_validator_output
#     for rule in apply_rules:
#         validator = rule.value(config)
#         if (
#             validator_output := validator.validate(file_validator.validated_content or {}, str(file_path))
#         ).get("valid", False) is False:
#             return merge_validation_outputs(file_validator_output, validator_output)

#     return file_validator_output
