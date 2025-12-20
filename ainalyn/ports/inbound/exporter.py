"""
Inbound port for exporting Agent Definitions.

This module defines the interface for exporting AgentDefinition
entities to various output formats (e.g., YAML).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition


class IDefinitionExporter(Protocol):
    """
    Interface for exporting Agent Definitions (Inbound Port).

    This protocol defines the contract for converting AgentDefinition
    entities into serialized string formats suitable for storage,
    transmission, or platform submission.

    Example:
        >>> class YamlExporter:
        ...     def export(self, definition: AgentDefinition) -> str:
        ...         # Convert to YAML string
        ...         ...
    """

    def export(self, definition: AgentDefinition) -> str:
        """
        Export an AgentDefinition to a string format.

        This method serializes the AgentDefinition into a string
        representation (e.g., YAML, JSON). The specific format
        depends on the implementation.

        Args:
            definition: The AgentDefinition to export.

        Returns:
            str: The serialized representation of the AgentDefinition.
                The format is implementation-specific (e.g., YAML).

        Raises:
            ExportError: If the definition cannot be serialized.
        """
        ...
