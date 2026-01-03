"""
Behavior Configuration for Agent execution characteristics.

This module defines the BehaviorConfig value object that describes
the execution behavior characteristics of an Agent.

According to the v0.2 specification, behavior configuration affects:
- Execution routing (Lite Route vs Heavy Route)
- Timeout handling
- Retry policies
- State management

Key fields per specification:
- is_long_running: Determines SYNC (Lite Route) vs ASYNC (Heavy Route)
- timeout_seconds: Maximum execution time before forced termination
- idempotent: Whether the Agent is safe to retry
- stateless: Whether the Agent maintains no state between invocations
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BehaviorConfig:
    """
    Configuration for Agent execution behavior.

    BehaviorConfig declares the expected execution characteristics
    of an Agent. Platform Core uses this information for:
    - Execution routing (Lite vs Heavy route selection)
    - Timeout enforcement
    - Retry policy application
    - Resource allocation

    Attributes:
        is_long_running: Whether this Agent requires long execution time.
            - False (default): Lite Route - Direct Lambda invoke, < 15 minutes
            - True: Heavy Route - Step Functions + SQS, > 15 minutes
            This affects the Core Dispatcher's routing decision.
        timeout_seconds: Maximum execution time in seconds.
            - Default: 300 (5 minutes)
            - Maximum depends on route: 900 for Lite, 86400 for Heavy
            After this time, execution is forcibly terminated.
        idempotent: Whether the Agent produces the same result for the same input.
            - True (default): Safe to retry on transient failures
            - False: Platform Core will not auto-retry
            Required for reliable execution in distributed systems.
        stateless: Whether the Agent maintains no persistent state.
            - True (default): No memory between invocations
            - False: May require special handling (not recommended)
            According to Platform Constitution, Agents should be stateless.

    Example - Standard short-running Agent:
        >>> config = BehaviorConfig()  # Uses defaults

    Example - Long-running Agent:
        >>> config = BehaviorConfig(
        ...     is_long_running=True,
        ...     timeout_seconds=3600,  # 1 hour
        ...     idempotent=True,
        ...     stateless=True,
        ... )

    Example - Non-idempotent Agent (use with caution):
        >>> config = BehaviorConfig(
        ...     idempotent=False,  # Will not be auto-retried
        ... )
    """

    is_long_running: bool = False
    timeout_seconds: int = 300
    idempotent: bool = True
    stateless: bool = True
