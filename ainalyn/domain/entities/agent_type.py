"""
Agent Type enumeration for v0.2 AWS MVP Edition.

This module defines the two types of Agents supported by the Ainalyn Platform:
- ATOMIC: Single-function execution units implemented with code
- COMPOSITE: Pure YAML workflow graph definitions

According to the v0.2 specification (03_agent_canonical_definition.md):
- Type A (ATOMIC): Code-First development, executed by Certified SDK Runtime
- Type B (COMPOSITE): Graph-First / Low-Code development, executed by Platform Core Graph Executor
"""

from __future__ import annotations

from enum import Enum


class AgentType(Enum):
    """
    Defines the type of Agent implementation.

    ATOMIC agents are implemented with code and executed by the
    Certified SDK Runtime. COMPOSITE agents are defined purely in YAML
    and executed by Platform Core's Graph Executor.

    Attributes:
        ATOMIC: Type A - Code-implemented single function execution unit.
            - Development: Code-First using SDK Decorator
            - Execution: Certified SDK Runtime
            - Contains: YAML Definition + Source Code

        COMPOSITE: Type B - Pure YAML workflow graph definition.
            - Development: Graph-First / Low-Code UI
            - Execution: Platform Core Graph Executor
            - Contains: YAML Definition only (no custom code)

    Example:
        >>> from ainalyn.domain.entities import AgentType
        >>> agent_type = AgentType.ATOMIC
        >>> print(agent_type.value)
        'ATOMIC'
    """

    ATOMIC = "ATOMIC"
    COMPOSITE = "COMPOSITE"
