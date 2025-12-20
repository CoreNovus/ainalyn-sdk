"""
Inbound port for validating Agent Definitions.

This module defines the interface and data structures for validating
AgentDefinition entities, including both schema validation and
static analysis.
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
            AgentDefinition can be submitted to the platform.
        WARNING: A non-blocking issue that should be reviewed
            but does not prevent submission.
    """

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class ValidationError:
    """
    A single validation issue found during validation.

    This immutable data class represents one validation error or
    warning, including its location, description, and severity.

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

    This immutable data class contains all validation errors and
    warnings found during the validation process, along with
    convenience methods for checking the overall result.

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
        Check if the validation passed (no ERROR-level issues).

        Returns:
            bool: True if there are no ERROR-level issues,
                False otherwise. Note that warnings do not
                affect this result.
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


class IDefinitionValidator(Protocol):
    """
    Interface for validating Agent Definitions (Inbound Port).

    This protocol defines the contract for validating AgentDefinition
    entities. Implementations should perform both structural validation
    (schema) and logical validation (static analysis).

    The validator does not modify the AgentDefinition; it only reports
    issues found during validation.

    Example:
        >>> class MyValidator:
        ...     def validate(self, definition: AgentDefinition) -> ValidationResult:
        ...         errors = []
        ...         # Perform validation checks
        ...         return ValidationResult(errors=tuple(errors))
    """

    def validate(self, definition: AgentDefinition) -> ValidationResult:
        """
        Validate an AgentDefinition and return the results.

        This method performs comprehensive validation including:
        - Schema validation (required fields, types, formats)
        - Static analysis (references, reachability, cycles)

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            ValidationResult: Contains all errors and warnings found.
                Use result.is_valid to check if validation passed.
        """
        ...
