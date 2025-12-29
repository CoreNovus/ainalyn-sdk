"""
Use case for validating Agent Definitions.

This module implements the validation use case that orchestrates
schema validation and static analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.application.ports.inbound.validate_agent_definition import (
    Severity,
    ValidationError,
    ValidationResult,
)

if TYPE_CHECKING:
    from ainalyn.application.ports.outbound.definition_schema_validation import (
        IDefinitionSchemaValidator,
    )
    from ainalyn.application.ports.outbound.definition_static_analysis import (
        IDefinitionAnalyzer,
    )
    from ainalyn.domain.entities import AgentDefinition


class ValidateDefinitionUseCase:
    """
    Use case for validating Agent Definitions.

    This use case orchestrates comprehensive validation by combining:
    1. Schema validation (structural correctness)
    2. Static analysis (logical consistency)

    The use case follows the principle that schema validation must
    complete successfully before static analysis runs, as logical
    analysis requires a structurally sound definition.

    Example:
        >>> from ainalyn.adapters.secondary import SchemaValidator, StaticAnalyzer
        >>> from ainalyn.application.use_cases import ValidateDefinitionUseCase
        >>> validator = SchemaValidator()
        >>> analyzer = StaticAnalyzer()
        >>> use_case = ValidateDefinitionUseCase(validator, analyzer)
        >>> result = use_case.execute(agent_definition)
        >>> if result.is_valid:
        ...     print("Validation passed!")
    """

    def __init__(
        self,
        schema_validator: IDefinitionSchemaValidator,
        static_analyzer: IDefinitionAnalyzer,
    ) -> None:
        """
        Initialize the validation use case.

        Args:
            schema_validator: The schema validator to use for structural checks.
            static_analyzer: The static analyzer to use for logical checks.
        """
        self._schema_validator = schema_validator
        self._static_analyzer = static_analyzer

    def execute(self, definition: AgentDefinition) -> ValidationResult:
        """
        Execute validation on an AgentDefinition.

        This method performs comprehensive validation in two phases:
        1. Schema validation - checks structural correctness
        2. Static analysis - checks logical consistency (only if schema passes)

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            ValidationResult: Contains all errors and warnings found.
                Use result.is_valid to check if validation passed.

        Note:
            Static analysis is only performed if schema validation
            produces no ERROR-level issues. Warnings do not prevent
            static analysis from running.
        """
        errors: list[ValidationError] = []

        # Phase 1: Schema validation
        schema_errors = self._schema_validator.validate_schema(definition)
        errors.extend(schema_errors)

        # Phase 2: Static analysis (only if no schema errors)
        has_schema_errors = any(e.severity == Severity.ERROR for e in schema_errors)
        if not has_schema_errors:
            analysis_issues = self._static_analyzer.analyze(definition)
            errors.extend(analysis_issues)

        return ValidationResult(errors=tuple(errors))
