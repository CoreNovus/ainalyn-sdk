"""
Outbound port for Agent Definition static analysis.

This module defines the interface for performing static analysis on
Agent Definitions, checking logical consistency and semantic correctness.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition
    from ainalyn.application.ports.inbound.validate_agent_definition import (
        ValidationError,
    )


class IDefinitionAnalyzer(Protocol):
    """
    Outbound port for static analysis of Agent Definitions.

    This port abstracts the capability to perform logical and semantic
    analysis on Agent Definitions. Static analysis checks relationships
    and consistency beyond structural validation.

    ⚠️ SDK BOUNDARY WARNING ⚠️

    This analysis checks logical correctness according to SDK rules.
    It does NOT represent platform execution validation. Platform Core
    applies additional governance and security checks during submission.

    Static analysis focuses on:
    - Reference validity (modules, prompts, tools exist)
    - Graph properties (DAG, reachability)
    - Naming uniqueness within scopes
    - Logical consistency

    Static analysis is distinct from schema validation:
    - Schema validation: Structural and type checks
    - Static analysis: Logical and semantic checks

    Example:
        >>> class StaticAnalyzer:
        ...     def analyze(
        ...         self, definition: AgentDefinition
        ...     ) -> tuple[ValidationError, ...]:
        ...         errors = []
        ...         # Check references, DAG, reachability
        ...         return tuple(errors)
    """

    def analyze(self, definition: AgentDefinition) -> tuple[ValidationError, ...]:
        """
        Perform static analysis on Agent Definition.

        This method checks the logical and semantic correctness of the
        Agent Definition, including reference validity, graph properties,
        and consistency.

        Args:
            definition: The AgentDefinition to analyze.

        Returns:
            tuple[ValidationError, ...]: Tuple of validation errors found.
                Empty tuple indicates analysis passed. Each error includes
                code, path, message, and severity.

        Note:
            This performs SDK-level static analysis only. Platform Core
            may apply additional checks during definition submission.
        """
        ...
