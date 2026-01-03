"""
State Reporter for Runtime Wrapper.

This module handles state reporting to Platform Core via DynamoDB
for ASYNC executions. For SYNC executions, state is returned
directly in the Lambda response.

According to EngSpec-diet:
- SYNC mode: SDK returns result directly, Platform Core writes to DynamoDB
- ASYNC mode: SDK writes directly to DynamoDB using DDB_TABLE_NAME

⚠️ PLATFORM BOUNDARY WARNING ⚠️
The SDK Runtime REPORTS state changes to Platform Core.
It does NOT have final authority over execution state.
Platform Core may override based on timeout, policy, etc.

⚠️ DEPENDENCY NOTE ⚠️
This module requires boto3 for DynamoDB access.
Install with: pip install ainalyn-sdk[runtime]
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ainalyn.domain.entities.execution_context import ExecutionContext
    from ainalyn.domain.entities.execution_result import StandardError


def get_iso_timestamp() -> str:
    """Get current timestamp in ISO 8601 format."""
    return datetime.now(UTC).isoformat()


def report_start(context: ExecutionContext) -> None:
    """
    Report execution start to Platform Core.

    For ASYNC mode, writes status=RUNNING to DynamoDB.
    For SYNC mode, this is a no-op (Platform Core handles it).

    Args:
        context: The execution context.
    """
    from ainalyn.domain.entities.execution_context import ExecutionMode

    if context.meta.mode == ExecutionMode.ASYNC:
        table_name = _get_async_table_name()
        _write_to_dynamodb(
            table_name=table_name,
            execution_id=context.meta.execution_id,
            update_data={
                "status": "RUNNING",
                "startedAt": get_iso_timestamp(),
                "agentId": context.meta.agent_id,
                "version": context.meta.version,
                "attempt": context.meta.attempt,
            },
        )


def report_success(
    context: ExecutionContext,
    output: dict[str, Any],
) -> None:
    """
    Report successful execution to Platform Core.

    For ASYNC mode, writes status=SUCCEEDED and output to DynamoDB.
    For SYNC mode, this is a no-op (result returned in Lambda response).

    Args:
        context: The execution context.
        output: The execution output.
    """
    from ainalyn.domain.entities.execution_context import ExecutionMode

    if context.meta.mode == ExecutionMode.ASYNC:
        table_name = _get_async_table_name()
        update_data: dict[str, Any] = {
            "status": "SUCCEEDED",
            "completedAt": get_iso_timestamp(),
            "updatedAt": get_iso_timestamp(),
        }

        # Store output (< 400KB in DynamoDB, else use S3)
        # For now, we assume output is small enough
        update_data["output"] = output

        _write_to_dynamodb(
            table_name=table_name,
            execution_id=context.meta.execution_id,
            update_data=update_data,
        )


def report_failure(
    context: ExecutionContext,
    error: StandardError,
) -> None:
    """
    Report failed execution to Platform Core.

    For ASYNC mode, writes status=FAILED and error to DynamoDB.
    For SYNC mode, this is a no-op (error returned in Lambda response).

    Args:
        context: The execution context.
        error: The error information.
    """
    from ainalyn.domain.entities.execution_context import ExecutionMode
    from ainalyn.runtime.errors import error_to_dict

    if context.meta.mode == ExecutionMode.ASYNC:
        table_name = _get_async_table_name()
        _write_to_dynamodb(
            table_name=table_name,
            execution_id=context.meta.execution_id,
            update_data={
                "status": "FAILED",
                "completedAt": get_iso_timestamp(),
                "updatedAt": get_iso_timestamp(),
                "error": error_to_dict(error),
            },
        )


def _write_to_dynamodb(
    table_name: str,
    execution_id: str,
    update_data: dict[str, Any],
) -> None:
    """
    Write execution state to DynamoDB.

    Uses conditional writes to ensure idempotency.

    Args:
        table_name: DynamoDB table name.
        execution_id: The execution ID (partition key).
        update_data: Data to write/update.
    """
    try:
        import boto3
    except ImportError as e:
        raise RuntimeError(
            "boto3 is required for ASYNC mode. "
            "Install with: pip install ainalyn-sdk[runtime]"
        ) from e

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    # Build update expression
    update_expr_parts = []
    expr_attr_names = {}
    expr_attr_values = {}

    for key, value in update_data.items():
        safe_key = f"#{key}"
        value_key = f":{key}"
        update_expr_parts.append(f"{safe_key} = {value_key}")
        expr_attr_names[safe_key] = key
        expr_attr_values[value_key] = value

    update_expression = "SET " + ", ".join(update_expr_parts)

    table.update_item(
        Key={"PK": f"EXEC#{execution_id}", "SK": "META"},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_values,
    )


def _get_async_table_name() -> str:
    """Get DynamoDB table name for ASYNC mode from env vars."""
    table_name = os.environ.get("DDB_TABLE_NAME")
    if not table_name:
        raise RuntimeError("DDB_TABLE_NAME env var is required for ASYNC mode.")
    return table_name
