"""
Context Parser for Runtime Wrapper.

This module parses the Worker Invocation Payload from Platform Core
into structured ExecutionContext objects.

According to v0.2 specification (05_platform_core_API_EIP_extension_standard.md),
the payload structure is:
{
    "meta": {"executionId", "agentId", "version", "attempt", "mode"},
    "security": {"userSub", "parentExecutionId"},
    "input": {...},
    "infra": {"resultTableName"}  // ASYNC only
}

⚠️ SDK BOUNDARY WARNING ⚠️
This module PARSES incoming context from Platform Core.
It does NOT generate execution IDs or make state decisions.
"""

from __future__ import annotations

from typing import Any

from ainalyn.domain.entities.execution_context import (
    ExecutionContext,
    ExecutionMeta,
    ExecutionMode,
    InfraContext,
    SecurityContext,
)


class ContextParseError(Exception):
    """Raised when the Platform Core payload cannot be parsed."""

    def __init__(self, field: str, reason: str) -> None:
        self.field = field
        self.reason = reason
        super().__init__(f"Failed to parse '{field}': {reason}")


def parse_event(event: dict[str, Any]) -> ExecutionContext:
    """
    Parse Platform Core Worker Invocation Payload.

    This function converts the raw Lambda event from Platform Core
    into a structured ExecutionContext for the handler.

    Args:
        event: The raw Lambda event dictionary from Platform Core.

    Returns:
        ExecutionContext: Parsed context with meta, security, input, and infra.

    Raises:
        ContextParseError: If required fields are missing or invalid.

    Example:
        >>> event = {
        ...     "meta": {
        ...         "executionId": "exec-12345",
        ...         "agentId": "pdf-parser",
        ...         "version": "1.0.0",
        ...         "attempt": 1,
        ...         "mode": "SYNC",
        ...     },
        ...     "security": {"userSub": "user-123"},
        ...     "input": {"file_url": "s3://..."},
        ... }
        >>> context = parse_event(event)
        >>> context.meta.execution_id
        'exec-12345'
    """
    # Parse meta section
    meta_dict = event.get("meta")
    if not isinstance(meta_dict, dict):
        raise ContextParseError("meta", "Missing or invalid 'meta' section")

    try:
        mode_str = meta_dict.get("mode", "SYNC")
        mode = ExecutionMode(mode_str)
    except ValueError:
        raise ContextParseError("meta.mode", f"Invalid mode: {mode_str}")

    meta = ExecutionMeta(
        execution_id=_require_str(meta_dict, "executionId", "meta"),
        agent_id=_require_str(meta_dict, "agentId", "meta"),
        version=_require_str(meta_dict, "version", "meta"),
        attempt=meta_dict.get("attempt", 1),
        mode=mode,
        start_time=meta_dict.get("startTime"),
    )

    # Parse security section
    security_dict = event.get("security")
    if not isinstance(security_dict, dict):
        raise ContextParseError("security", "Missing or invalid 'security' section")

    # Parse permissions (optional, defaults to empty tuple)
    permissions_list = security_dict.get("permissions", [])
    if not isinstance(permissions_list, list):
        permissions_list = []
    permissions = tuple(str(p) for p in permissions_list if p)

    security = SecurityContext(
        user_sub=_require_str(security_dict, "userSub", "security"),
        permissions=permissions,
        parent_execution_id=security_dict.get("parentExecutionId"),
    )

    # Parse input section
    input_data = event.get("input")
    if input_data is None:
        input_data = {}
    elif not isinstance(input_data, dict):
        raise ContextParseError("input", "Input must be a dictionary")

    # Parse infra section (ASYNC only)
    infra = None
    infra_dict = event.get("infra")
    if infra_dict and isinstance(infra_dict, dict):
        table_name = infra_dict.get("resultTableName")
        if table_name:
            infra = InfraContext(result_table_name=table_name)

    return ExecutionContext(
        meta=meta,
        security=security,
        input_data=input_data,
        infra=infra,
    )


def _require_str(d: dict[str, Any], key: str, section: str) -> str:
    """Extract a required string field from a dictionary."""
    value = d.get(key)
    if value is None:
        msg = f"{section}.{key}"
        raise ContextParseError(msg, "Required field is missing")
    if not isinstance(value, str):
        msg = f"{section}.{key}"
        raise ContextParseError(msg, "Field must be a string")
    return value
