"""
Outbound port for schema validation.

This module defines the interface for validating the structure
and types of AgentDefinition entities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition
    from ainalyn.ports.inbound.validator import ValidationError


class ISchemaValidator(Protocol):
    """
    Interface for schema validation (Outbound Port).

    This protocol defines the contract for validating the structural
    correctness of AgentDefinition entities. It checks for required
    fields, type correctness, format compliance, and naming conventions.

    Schema validation is distinct from static analysis:
    - Schema validation: Structural and type checks
    - Static analysis: Logical checks (references, cycles, reachability)

    Implementations are Secondary Adapters that may use various
    validation strategies (e.g., JSON Schema, custom rules).

    Example:
        >>> class JsonSchemaValidator:
        ...     def validate_schema(
        ...         self, definition: AgentDefinition
        ...     ) -> list[ValidationError]:
        ...         errors = []
        ...         # Check required fields, types, formats
        ...         return errors
    """

    def validate_schema(self, definition: AgentDefinition) -> list[ValidationError]:
        """
        Validate the schema of an AgentDefinition.

        This method checks the structural correctness of the
        AgentDefinition, including:
        - Required fields are present
        - Field types are correct
        - Field values match expected formats (e.g., semver, name pattern)
        - Nested structures are valid

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            list[ValidationError]: A list of validation errors found.
                Empty list indicates the schema is valid.
                Each error includes code, path, message, and severity.
        """
        ...
