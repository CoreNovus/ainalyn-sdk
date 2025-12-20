"""
Outbound port for writing Agent Definitions.

This module defines the interface for writing AgentDefinition
content to external destinations (e.g., files).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.domain.entities import AgentDefinition


class IDefinitionWriter(Protocol):
    """
    Interface for writing Agent Definitions (Outbound Port).

    This protocol defines the contract for serializing and writing
    AgentDefinition entities to external storage. It is implemented
    by Secondary Adapters such as YAML file writers.

    The interface separates serialization (export) from persistence
    (write), allowing flexible composition of these operations.

    Example:
        >>> class YamlFileWriter:
        ...     def export(self, definition: AgentDefinition) -> str:
        ...         # Convert to YAML string
        ...         ...
        ...     def write(self, content: str, path: Path) -> None:
        ...         # Write to file
        ...         path.write_text(content)
    """

    def export(self, definition: AgentDefinition) -> str:
        """
        Serialize an AgentDefinition to a string format.

        This method converts the AgentDefinition into a string
        representation suitable for storage or transmission.

        Args:
            definition: The AgentDefinition to serialize.

        Returns:
            str: The serialized content (e.g., YAML string).

        Raises:
            SerializationError: If serialization fails.
        """
        ...

    def write(self, content: str, path: Path) -> None:
        """
        Write serialized content to a file.

        This method persists the given content to the specified
        file path. Parent directories are created if they do not
        exist.

        Args:
            content: The serialized content to write.
            path: The destination file path.

        Raises:
            IOError: If the file cannot be written.
            PermissionError: If write permission is denied.
        """
        ...
