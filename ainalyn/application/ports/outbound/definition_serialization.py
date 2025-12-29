"""
Outbound port for Agent Definition serialization.

This module defines the interface for serializing Agent Definitions
to various formats (YAML, JSON, etc.).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition


class IDefinitionSerializer(Protocol):
    """
    Outbound port for serializing Agent Definitions.

    This port abstracts the capability to convert Agent Definitions into
    external formats for storage, transmission, or platform submission.

    ⚠️ SDK BOUNDARY WARNING ⚠️

    This serialization creates a DESCRIPTION of an agent for platform
    submission. The serialized output does NOT execute by itself.
    Execution is handled exclusively by Platform Core.

    Serializers should include appropriate headers/comments warning that:
    - This is a description, not an executable
    - Platform Core has sole authority over execution
    - SDK validation ≠ Platform will execute this definition

    Example:
        >>> class YamlSerializer:
        ...     def serialize(self, definition: AgentDefinition) -> str:
        ...         # Convert to YAML with appropriate headers
        ...         return yaml_string
    """

    def serialize(self, definition: AgentDefinition) -> str:
        """
        Serialize Agent Definition to string format.

        This method converts an Agent Definition into a string representation
        suitable for storage or transmission. The format should be human-readable
        and include appropriate boundary warnings.

        Args:
            definition: The AgentDefinition to serialize.

        Returns:
            str: The serialized representation of the definition.

        Raises:
            SerializationError: If serialization fails due to invalid data.

        Note:
            The serialized output is a description for platform submission,
            not an executable. Platform Core controls all execution.
        """
        ...
