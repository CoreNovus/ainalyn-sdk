"""
Review Feedback Value Object.

This module defines feedback provided by Platform Core during the
review process of an Agent Definition submission.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FeedbackSeverity(Enum):
    """
    Severity level of review feedback.

    This enum categorizes feedback from Platform Core's review process,
    helping developers prioritize issues.

    Attributes:
        ERROR: A blocking issue that prevents acceptance. Must be fixed
            before the agent can be approved.
        WARNING: A non-blocking issue that should be addressed but does
            not prevent approval. May affect quality or performance.
        INFO: Informational feedback, suggestions, or recommendations
            for improvement. Does not affect approval.

    Example:
        >>> severity = FeedbackSeverity.ERROR
        >>> print(severity.value)
        error
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class FeedbackCategory(Enum):
    """
    Category of review feedback.

    Categorizes feedback by the type of issue or concern raised
    during Platform Core's review process.

    Attributes:
        SECURITY: Security-related issues (e.g., unsafe tool usage,
            permission requirements, data handling).
        COMPLIANCE: Policy and governance compliance (e.g., terms of
            service violations, restricted content).
        QUALITY: Code quality, documentation, or usability issues.
        PERFORMANCE: Performance concerns (e.g., resource usage,
            inefficient workflows).
        COMPATIBILITY: Compatibility issues with platform standards
            or other agents.
        GENERAL: General feedback that doesn't fit other categories.

    Example:
        >>> category = FeedbackCategory.SECURITY
        >>> print(category.value)
        security
    """

    SECURITY = "security"
    COMPLIANCE = "compliance"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    COMPATIBILITY = "compatibility"
    GENERAL = "general"


@dataclass(frozen=True, slots=True)
class ReviewFeedback:
    """
    Feedback from Platform Core during agent review.

    This immutable value object represents a single piece of feedback
    provided by Platform Core's review and governance process.

    Per Platform Constitution (rule-docs/Platform Vision & System Boundary.md):
    - Platform Core has final authority over agent acceptance
    - Feedback is provided to help developers meet platform standards
    - SDK validation success ≠ Platform Core acceptance

    Attributes:
        category: The category of this feedback (security, quality, etc.).
        severity: The severity level (error, warning, info).
        message: Human-readable description of the issue or suggestion.
        path: Optional JSON Path to the specific location in the agent
            definition where the issue was found. Examples:
            - "workflows[0].nodes[2]"
            - "tools[0].input_schema"
            - "agent.description"
            None if feedback applies to the entire definition.
        code: Optional machine-readable error code for programmatic
            handling. Examples: "SEC001", "QUAL100", "PERF050".

    Example:
        >>> feedback = ReviewFeedback(
        ...     category=FeedbackCategory.SECURITY,
        ...     severity=FeedbackSeverity.ERROR,
        ...     message="Tool 'file-writer' requires explicit permission",
        ...     path="tools[0]",
        ...     code="SEC001"
        ... )
        >>> print(f"[{feedback.severity.value}] {feedback.message}")
        [error] Tool 'file-writer' requires explicit permission
    """

    category: FeedbackCategory
    severity: FeedbackSeverity
    message: str
    path: str | None = None
    code: str | None = None

    def is_blocking(self) -> bool:
        """
        Check if this feedback is blocking (prevents approval).

        Only ERROR-severity feedback blocks approval.

        Returns:
            bool: True if this feedback prevents approval.

        Example:
            >>> error_feedback = ReviewFeedback(
            ...     category=FeedbackCategory.SECURITY,
            ...     severity=FeedbackSeverity.ERROR,
            ...     message="Critical issue"
            ... )
            >>> error_feedback.is_blocking()
            True
            >>> warning_feedback = ReviewFeedback(
            ...     category=FeedbackCategory.QUALITY,
            ...     severity=FeedbackSeverity.WARNING,
            ...     message="Consider improvement"
            ... )
            >>> warning_feedback.is_blocking()
            False
        """
        return self.severity == FeedbackSeverity.ERROR

    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            str: Formatted feedback message.

        Example:
            >>> feedback = ReviewFeedback(
            ...     category=FeedbackCategory.QUALITY,
            ...     severity=FeedbackSeverity.WARNING,
            ...     message="Consider adding more examples",
            ...     path="agent.description"
            ... )
            >>> print(feedback)
            [quality/warning] agent.description: Consider adding more examples
        """
        parts = [f"[{self.category.value}/{self.severity.value}]"]
        if self.path:
            parts.append(f"{self.path}:")
        parts.append(self.message)
        if self.code:
            parts.append(f"({self.code})")
        return " ".join(parts)
