"""
Decorator API for Runtime Wrapper.

This module provides the @agent.atomic() decorator for registering
ATOMIC agent handlers with the SDK Runtime.

The decorator wraps the user's handler function to:
1. Parse the Platform Core payload
2. Report execution start (ASYNC mode)
3. Execute the user's handler
4. Translate errors to standard format
5. Report execution result (ASYNC mode)

⚠️ SDK BOUNDARY WARNING ⚠️
This decorator creates a BRIDGE between developer code and Platform Core.
The SDK does NOT execute agents autonomously.
All execution is triggered by Platform Core.

Usage:
    from ainalyn.runtime import agent

    @agent.atomic(name="pdf-parser")
    def handler(input_data: dict) -> dict:
        # Process input and return output
        return {"text": "extracted content"}
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from ainalyn.domain.entities.execution_context import ExecutionMode
from ainalyn.runtime.context import ContextParseError, parse_event
from ainalyn.runtime.errors import error_to_dict, translate_exception
from ainalyn.runtime.state_reporter import (
    get_iso_timestamp,
    report_failure,
    report_start,
    report_success,
)

# Type variables for handler signatures
T = TypeVar("T")
HandlerFunc = Callable[[dict[str, Any]], dict[str, Any]]
LambdaHandler = Callable[[dict[str, Any], Any], dict[str, Any]]


class Agent:
    """
    Agent Runtime Wrapper.

    Provides decorators for registering ATOMIC agent handlers.

    Example:
        >>> agent = Agent()
        >>>
        >>> @agent.atomic(name="my-tool")
        ... def handler(input_data: dict) -> dict:
        ...     return {"result": "success"}
        >>>
        >>> # The decorated handler is Lambda-compatible
        >>> response = handler(event, context)
    """

    def atomic(
        self,
        name: str,
        *,
        version: str = "1.0.0",
    ) -> Callable[[HandlerFunc], LambdaHandler]:
        """
        Decorator for ATOMIC agent handlers.

        Wraps a simple handler function to be compatible with
        Platform Core's Lambda invocation protocol.

        The decorated function will:
        1. Parse the incoming Platform Core event
        2. Report RUNNING state (ASYNC mode)
        3. Call the user's handler with input_data
        4. Report SUCCEEDED/FAILED state (ASYNC mode)
        5. Return the appropriate Lambda response

        Args:
            name: The agent name (must match AgentDefinition.name).
            version: The agent version (default: "1.0.0").

        Returns:
            Callable: A decorator function.

        Example:
            >>> @agent.atomic(name="pdf-parser")
            ... def handler(input_data: dict) -> dict:
            ...     url = input_data.get("file_url")
            ...     text = extract_pdf(url)
            ...     return {"text": text}
        """

        def decorator(func: HandlerFunc) -> LambdaHandler:
            @wraps(func)
            def wrapper(event: dict[str, Any], context: Any = None) -> dict[str, Any]:
                started_at = get_iso_timestamp()

                # 1. Parse Platform Core event
                try:
                    exec_context = parse_event(event)
                except ContextParseError as e:
                    # Invalid payload - return error without state reporting
                    return {
                        "status": "FAILED",
                        "error": {
                            "code": "CONTEXT_PARSE_ERROR",
                            "message": str(e),
                            "retryable": False,
                        },
                    }

                # 2. Report RUNNING state (ASYNC mode)
                try:
                    report_start(exec_context)
                except Exception:
                    # State reporting failure shouldn't stop execution
                    pass

                # 3. Execute user handler
                try:
                    raw_output = func(exec_context.input_data)

                    # Validate output is a dict (runtime safety check)
                    if not isinstance(raw_output, dict):
                        output = {"result": raw_output}
                    else:
                        output = raw_output

                    # 4. Report SUCCESS (ASYNC mode)
                    with contextlib.suppress(Exception):
                        report_success(exec_context, output)

                    # 5. Return Lambda response
                    if exec_context.meta.mode == ExecutionMode.ASYNC:
                        return {}
                    return {
                        "status": "SUCCEEDED",
                        "output": output,
                        "startedAt": started_at,
                        "completedAt": get_iso_timestamp(),
                    }

                except Exception as e:
                    # 4. Translate error
                    error = translate_exception(e)

                    # 5. Report FAILURE (ASYNC mode)
                    with contextlib.suppress(Exception):
                        report_failure(exec_context, error)

                    # 6. Return Lambda response
                    if exec_context.meta.mode == ExecutionMode.ASYNC:
                        return {}
                    return {
                        "status": "FAILED",
                        "error": error_to_dict(error),
                        "startedAt": started_at,
                        "completedAt": get_iso_timestamp(),
                    }

            # Store metadata on the wrapper
            wrapper._ainalyn_agent_name = name  # type: ignore[attr-defined]
            wrapper._ainalyn_agent_version = version  # type: ignore[attr-defined]

            return wrapper

        return decorator


# Global agent instance for convenience
agent = Agent()
