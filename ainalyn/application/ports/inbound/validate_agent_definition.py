"""
Inbound port for Agent Definition validation use case.

This module defines the interface and data structures for the
validation use case, including ValidationResult and ValidationError.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition


class Severity(Enum):
    """
    Severity level of a validation issue.

    This enum categorizes validation issues by their severity,
    helping users distinguish between blocking errors and
    informational warnings.

    Attributes:
        ERROR: A blocking issue that must be fixed before the
            AgentDefinition can be considered valid by SDK rules.
        WARNING: A non-blocking issue that should be reviewed
            but does not prevent local validation from passing.
    """

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class ValidationError:
    """
    A single validation issue found during validation.

    This immutable data class represents one validation error or
    warning, including its location, description, and severity.

    Note: This is NOT a Python exception. It's a data structure
    representing validation feedback.

    Attributes:
        code: A unique error code identifying the type of issue.
            Examples: "MISSING_REQUIRED_FIELD", "INVALID_REFERENCE",
            "CIRCULAR_DEPENDENCY". Used for programmatic handling.
        path: JSON Path-style location of the issue within the
            AgentDefinition structure. Examples: "agent.version",
            "workflows[0].nodes[1].reference".
        message: Human-readable description of the issue, suitable
            for display to developers.
        severity: The severity level of this issue (ERROR or WARNING).
            Defaults to ERROR.

    Example:
        >>> error = ValidationError(
        ...     code="MISSING_REQUIRED_FIELD",
        ...     path="agent.version",
        ...     message="Required field 'version' is missing",
        ...     severity=Severity.ERROR,
        ... )
    """

    code: str
    path: str
    message: str
    severity: Severity = Severity.ERROR


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    The complete result of validating an AgentDefinition.

    ⚠️ CRITICAL PLATFORM BOUNDARY WARNING ⚠️

    SDK validation success does NOT guarantee platform execution.
    The Ainalyn Platform applies additional checks during submission:
    - Governance policies
    - Security scanning
    - Resource quota validation
    - Marketplace compliance

    This validation only ensures the definition is structurally
    and semantically correct according to SDK rules.

    Per platform constitution: "Local compilation ≠ Platform execution"
    See: https://docs.ainalyn.io/sdk/platform-boundaries/

    Attributes:
        errors: Tuple of all validation issues found, including
            both errors and warnings.

    Example:
        >>> result = ValidationResult(errors=(
        ...     ValidationError(
        ...         code="MISSING_ENTRY_NODE",
        ...         path="workflows[0]",
        ...         message="Workflow 'main' has no entry_node specified",
        ...     ),
        ... ))
        >>> result.is_valid
        False
    """

    errors: tuple[ValidationError, ...]

    @property
    def is_valid(self) -> bool:
        """
        Check if SDK validation passed (no ERROR-level issues).

        ⚠️ IMPORTANT: Passing SDK validation does NOT mean:
        - Platform will accept the definition
        - Platform will execute the agent
        - Agent will be listed in marketplace

        Platform Core has final authority over all executions and
        applies additional validation during submission.

        Returns:
            bool: True if there are no ERROR-level issues according
                to SDK rules, False otherwise. Note that warnings do
                not affect this result.
        """
        return not any(e.severity == Severity.ERROR for e in self.errors)

    @property
    def has_warnings(self) -> bool:
        """
        Check if there are any WARNING-level issues.

        Returns:
            bool: True if there is at least one WARNING-level
                issue, False otherwise.
        """
        return any(e.severity == Severity.WARNING for e in self.errors)


class IValidateAgentDefinition(Protocol):
    """
    Inbound port for validating Agent Definitions.

    This port represents the validation use case. It defines what the
    application can do: validate an Agent Definition and return results.

    ⚠️ SDK BOUNDARY WARNING ⚠️

    This validation checks SDK-level correctness only. Platform Core
    applies additional validation during submission. SDK validation
    success ≠ Platform execution.

    Implementations coordinate both schema validation and static analysis
    to provide comprehensive feedback on the definition.

    Example:
        >>> class ValidateDefinitionUseCase:
        ...     def execute(self, definition: AgentDefinition) -> ValidationResult:
        ...         # Coordinate schema validation and static analysis
        ...         return ValidationResult(errors=all_errors)
    """

    def execute(self, definition: AgentDefinition) -> ValidationResult:
        """
        Execute the validation use case.

        This method validates an Agent Definition by coordinating
        schema validation and static analysis.

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            ValidationResult: Contains all errors and warnings found.
                Use result.is_valid to check if SDK validation passed.

        Note:
            SDK validation success does NOT guarantee platform acceptance
            or execution. Platform Core applies additional checks.
        """
        ...
