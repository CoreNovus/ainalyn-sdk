"""
Error Handling for Runtime Wrapper.

This module provides utilities for translating Python exceptions
into the standard error format expected by Platform Core.

According to v0.2 specification, errors must be translated to
a standard structure for Platform Core to process and categorize.

⚠️ SDK BOUNDARY WARNING ⚠️
Error translation is for REPORTING to Platform Core.
The SDK does NOT decide retry policy or billing impact.
Platform Core makes all final decisions.
"""

from __future__ import annotations

import traceback
from typing import Any

from ainalyn.domain.entities.execution_result import StandardError


class HandlerError(Exception):
    """
    Base exception for handler errors.

    Handlers can raise this exception with structured error information
    that will be properly translated for Platform Core.

    Attributes:
        code: Error code (e.g., "INPUT_INVALID", "EXTERNAL_SERVICE_ERROR").
        message: Human-readable error message.
        details: Additional error details.
        retryable: Whether this error is safe to retry.
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
        self.retryable = retryable


class InputValidationError(HandlerError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="INPUT_INVALID",
            message=message,
            details=details,
            retryable=False,
        )


class ExternalServiceError(HandlerError):
    """Raised when an external service call fails."""

    def __init__(
        self,
        service: str,
        message: str,
        retryable: bool = True,
    ) -> None:
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message=message,
            details={"service": service},
            retryable=retryable,
        )


class TimeoutError(HandlerError):
    """Raised when an operation times out."""

    def __init__(self, message: str = "Operation timed out") -> None:
        super().__init__(
            code="TIMEOUT",
            message=message,
            retryable=True,
        )


def translate_exception(exc: Exception) -> StandardError:
    """
    Translate a Python exception to StandardError format.

    This function converts any exception into the standard error
    format that Platform Core expects.

    Args:
        exc: The exception to translate.

    Returns:
        StandardError: The translated error object.
    """
    # Handle structured HandlerError
    if isinstance(exc, HandlerError):
        return StandardError(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            retryable=exc.retryable,
            stack_trace=traceback.format_exc(),
        )

    # Handle common Python exceptions
    if isinstance(exc, ValueError):
        return StandardError(
            code="VALUE_ERROR",
            message=str(exc),
            retryable=False,
            stack_trace=traceback.format_exc(),
        )

    if isinstance(exc, TypeError):
        return StandardError(
            code="TYPE_ERROR",
            message=str(exc),
            retryable=False,
            stack_trace=traceback.format_exc(),
        )

    if isinstance(exc, KeyError):
        return StandardError(
            code="KEY_ERROR",
            message=f"Missing key: {exc}",
            retryable=False,
            stack_trace=traceback.format_exc(),
        )

    if isinstance(exc, ConnectionError):
        return StandardError(
            code="CONNECTION_ERROR",
            message=str(exc),
            retryable=True,
            stack_trace=traceback.format_exc(),
        )

    # Default: unknown error
    return StandardError(
        code=type(exc).__name__.upper(),
        message=str(exc) or "An unexpected error occurred",
        retryable=False,
        stack_trace=traceback.format_exc(),
    )


def error_to_dict(error: StandardError) -> dict[str, Any]:
    """
    Convert StandardError to dictionary for JSON serialization.

    Args:
        error: The StandardError to convert.

    Returns:
        dict: Dictionary representation for Platform Core.
    """
    result: dict[str, Any] = {
        "code": error.code,
        "message": error.message,
        "retryable": error.retryable,
    }

    if error.details:
        result["details"] = error.details

    if error.stack_trace:
        result["stackTrace"] = error.stack_trace

    return result
