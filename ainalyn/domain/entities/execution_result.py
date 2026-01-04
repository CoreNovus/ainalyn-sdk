"""
Execution Result for Runtime Wrapper.

This module defines the ExecutionResult and related entities that
represent the result of an Agent execution.

According to v0.2 specification (02_execution_state_storage_transition_model.md),
terminal states are:
- SUCCEEDED: Full billing applies
- FAILED: May have partial billing
- ABORTED: Prorated billing based on progress

IMPORTANT: This is for SDK Runtime to REPORT results back to
Platform Core. The actual state transition authority belongs
to Platform Core exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlatformErrors(str, Enum):
    """
    Standard error codes from Platform Core.

    According to 00_global_types.py specification, these are
    the standard error codes that Platform Core may return.

    Attributes:
        TIMEOUT: Platform timeout occurred.
        INTERNAL_ERROR: Platform internal error.
        USER_INPUT_INVALID: User input validation failed.
    """

    TIMEOUT = "PLATFORM_TIMEOUT"
    INTERNAL_ERROR = "PLATFORM_INTERNAL_ERROR"
    USER_INPUT_INVALID = "USER_INPUT_INVALID"


class ExecutionStatus(Enum):
    """
    Execution status for SDK Runtime reporting.

    According to Platform Constitution, only Platform Core can
    make final decisions on execution state. SDK Runtime uses
    these statuses to REPORT to Platform Core.

    Attributes:
        REQUESTED: Execution request just received.
            Initial state when task is accepted.
        RUNNING: Execution is in progress.
            Reported at start of handler execution.
        SUCCEEDED: Execution completed successfully.
            Terminal state. Full billing applies.
        FAILED: Execution failed.
            Terminal state. Billing depends on failure type.
        ABORTED: Execution cancelled by user.
            Terminal state. Prorated billing based on progress.
    """

    REQUESTED = "REQUESTED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


@dataclass(frozen=True, slots=True)
class StandardError:
    """
    Standard error format for execution failures.

    According to v0.2 specification, errors must be translated
    to a standard format for Platform Core to process.

    Attributes:
        code: Error code (e.g., "INPUT_INVALID", "TIMEOUT").
        message: Human-readable error message.
        details: Additional error details (optional).
        stack_trace: Stack trace for debugging (optional).
        retryable: Whether this error is retryable.
    """

    code: str
    message: str
    details: dict[str, Any] | None = None
    stack_trace: str | None = None
    retryable: bool = False


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """
    Result of an Agent execution.

    ExecutionResult encapsulates the outcome of a handler execution.
    The SDK Runtime uses this to report back to Platform Core.

    IMPORTANT - State Authority:
    - SDK Runtime REPORTS this result
    - Platform Core DECIDES the actual state
    - Platform Core may override based on timeout, policy, etc.

    Attributes:
        status: The reported execution status.
        output: Output data from successful execution.
            Must conform to the Agent's output_schema.
        error: Error information for failed execution.
        started_at: ISO 8601 timestamp when execution started.
        completed_at: ISO 8601 timestamp when execution completed.
        progress_percent: Progress percentage (0-100) for long-running tasks.
        evidence_pointers: S3 keys for large output artifacts.

    Example - Success:
        >>> result = ExecutionResult(
        ...     status=ExecutionStatus.SUCCEEDED,
        ...     output={"text": "Extracted PDF content..."},
        ...     completed_at="2026-01-03T10:30:00Z",
        ... )

    Example - Failure:
        >>> result = ExecutionResult(
        ...     status=ExecutionStatus.FAILED,
        ...     error=StandardError(
        ...         code="INPUT_INVALID",
        ...         message="PDF file is corrupted",
        ...         retryable=False,
        ...     ),
        ...     completed_at="2026-01-03T10:30:00Z",
        ... )
    """

    status: ExecutionStatus
    output: dict[str, Any] | None = None
    error: StandardError | None = None
    started_at: str | None = None
    completed_at: str | None = None
    progress_percent: int | None = None
    evidence_pointers: tuple[str, ...] = field(default_factory=tuple)
