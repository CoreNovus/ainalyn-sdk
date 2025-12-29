"""
Outbound port for Agent Definition schema validation.

This module defines the interface for validating the structural
correctness of Agent Definitions. Implementations may use JSON Schema,
custom validators, or other mechanisms.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition
    from ainalyn.application.ports.inbound.validate_agent_definition import (
        ValidationError,
    )


class IDefinitionSchemaValidator(Protocol):
    """
    Outbound port for validating Agent Definition schemas.

    This port abstracts the capability to validate that an Agent Definition
    conforms to structural requirements. Implementations may use JSON Schema,
    custom validators, or other mechanisms.

    ⚠️ SDK BOUNDARY WARNING ⚠️

    This validation checks the structural correctness of the definition
    according to SDK rules. It does NOT represent platform execution validation.
    Platform Core applies additional checks during submission.

    Schema validation focuses on:
    - Required fields are present
    - Field types are correct
    - Field values match expected formats (semver, naming patterns)
    - Nested structures are valid

    Schema validation is distinct from static analysis:
    - Schema validation: Structural and type checks
    - Static analysis: Logical checks (references, cycles, reachability)

    Example:
        >>> class SchemaValidator:
        ...     def validate_schema(
        ...         self, definition: AgentDefinition
        ...     ) -> tuple[ValidationError, ...]:
        ...         errors = []
        ...         # Perform structural validation
        ...         return tuple(errors)
    """

    def validate_schema(
        self, definition: AgentDefinition
    ) -> tuple[ValidationError, ...]:
        """
        Validate Agent Definition structure.

        This method checks the structural correctness of the Agent Definition,
        ensuring it conforms to the SDK's schema requirements.

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            tuple[ValidationError, ...]: Tuple of validation errors found.
                Empty tuple indicates schema is valid. Each error includes
                code, path, message, and severity.

        Note:
            This validates SDK schema compliance only. Platform Core may
            apply additional validation during definition submission.
        """
        ...
