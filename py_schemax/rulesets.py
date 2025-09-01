from enum import Enum
from pathlib import Path

from py_schemax import config
from py_schemax.config import Config
from py_schemax.schema.validation import ValidationOutputSchema
from py_schemax.utils import merge_validation_outputs
from py_schemax.validator import (
    DependentsSchemaValidator,
    DependsOnSchemaValidator,
    FileValidator,
    PydanticSchemaValidator,
    UniqueFQNValidator,
)


class ValidationRuleSetEnum(Enum):
    RV_SCHEMA = PydanticSchemaValidator
    RV_UNIQUE_FQN = UniqueFQNValidator
    RV_DEPENDS_ON = DependsOnSchemaValidator
    RV_DEPENDENTS = DependentsSchemaValidator


DEFAULT_RULESETS = (ValidationRuleSetEnum.RV_SCHEMA,)


class RuleSetBasedValidation:
    def __init__(
        self, config: Config, apply_rules: list[ValidationRuleSetEnum]
    ) -> None:
        self.__config = config
        self.__validators = [rule.value(config) for rule in apply_rules]

    def pre_validate_all(self) -> None:
        """Call pre_validate_all on all validators."""
        for validator in self.__validators:
            validator.pre_validate_all()

    def post_validate_all(self, exit_code: int) -> None:
        """Call post_validate_all on all validators.

        Args:
            exit_code: Final exit code indicating validation success/failure
        """
        for validator in self.__validators:
            validator.post_validate_all(exit_code=exit_code)

    def validate_file(self, file_path: str | Path) -> ValidationOutputSchema:
        # Phase 0: check if provided file is valid, and parse json/yaml file to dict
        file_validator = FileValidator(self.__config)
        if (file_validator_output := file_validator.validate(file_path)).get(
            "valid", False
        ) is False:
            return file_validator_output

        # Phase 1: Call pre_validate on all validators
        for validator in self.__validators:
            validator.pre_validate(
                file_validator.validated_content or {}, str(file_path)
            )

        # Phase 2: Perform validation on all validators
        final_output = file_validator_output
        for validator in self.__validators:
            validator_output = validator.validate(
                file_validator.validated_content or {}, str(file_path)
            )
            if validator_output.get("valid", False) is False:
                final_output = merge_validation_outputs(final_output, validator_output)

        # Phase 3: Call post_validate on all validators with the final merged output
        for validator in self.__validators:
            validator.post_validate(
                file_validator.validated_content or {},
                str(file_path),
                validation_output=final_output,
            )

        return final_output
