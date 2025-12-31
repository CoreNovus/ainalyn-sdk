"""
EIP Dependency declaration for Agent Definitions.

This module defines the EIPDependency entity that allows developers
to declare which Execution Implementation Providers (EIPs) their
Agent depends on, along with configuration hints for Platform Core.

IMPORTANT: This is a DECLARATION only. The actual EIP invocation
is handled exclusively by Platform Core during Execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class EIPBinding:
    """
    Binds a Tool/Module to a specific EIP provider and service.

    EIPBinding declares which EIP should be used to implement
    a Tool or Module. This is a description for Platform Core,
    not an execution directive.

    Attributes:
        provider: The EIP provider identifier (e.g., "openai", "azure", "local").
        service: The specific service within the provider (e.g., "whisper", "gpt-4").

    Example:
        >>> binding = EIPBinding(
        ...     provider="openai",
        ...     service="whisper",
        ... )
    """

    provider: str
    service: str


@dataclass(frozen=True, slots=True)
class EIPDependency:
    """
    Declares an EIP dependency for the Agent Definition.

    EIPDependency represents a declaration that the Agent requires
    a specific EIP to be available for execution. This allows
    Platform Core to validate EIP availability during review
    and properly route execution requests.

    This is a pure declaration entity with no execution semantics.
    Platform Core uses this information for:
    - Review Gate 5: EIP dependency validation
    - Execution routing to appropriate EIP instances
    - Capability matching and version compatibility

    Attributes:
        provider: The EIP provider identifier (e.g., "openai", "azure", "local").
            Must match a registered provider in Platform Core.
        service: The specific service within the provider (e.g., "whisper", "gpt-4").
        version: Version constraint for the EIP (e.g., ">=1.0.0", "^2.0.0").
            Uses semver-compatible constraint syntax.
        config_hints: Configuration hints for Platform Core. These are
            suggestions that Platform Core may use when invoking the EIP.
            Common hints include:
            - streaming: bool - Whether to use streaming mode
            - model: str - Specific model to use
            - timeout: int - Suggested timeout in seconds
            - region: str - Preferred deployment region

    Example:
        >>> dependency = EIPDependency(
        ...     provider="openai",
        ...     service="whisper",
        ...     version=">=1.0.0",
        ...     config_hints={
        ...         "streaming": True,
        ...         "model": "whisper-1",
        ...         "language": "zh",
        ...     },
        ... )
    """

    provider: str
    service: str
    version: str = "*"
    config_hints: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CompletionCriteria:
    """
    Defines the success and failure criteria for an Agent.

    CompletionCriteria provides explicit definitions of what constitutes
    a successful or failed execution. This is required by Platform Core
    to validate that the Agent has a determinable completion state.

    According to the Platform Constitution:
    - Agent must have "可判定的完成/失敗狀態"
    - Execution result must be verifiable

    Attributes:
        success: Description of what constitutes successful completion.
        failure: Description of what constitutes failure.

    Example:
        >>> criteria = CompletionCriteria(
        ...     success="Audio successfully transcribed with timestamps",
        ...     failure="Audio format not supported or unrecognizable",
        ... )
    """

    success: str
    failure: str
