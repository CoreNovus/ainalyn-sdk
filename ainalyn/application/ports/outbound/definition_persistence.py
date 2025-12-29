"""
Outbound port for Agent Definition persistence.

This module defines the interface for writing Agent Definitions
to persistent storage (files, databases, etc.).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path


class IDefinitionWriter(Protocol):
    """
    Outbound port for persisting Agent Definitions.

    This port abstracts the capability to write serialized Agent Definitions
    to persistent storage. Implementations may write to local files, remote
    storage, databases, or other persistence mechanisms.

    ⚠️ SDK BOUNDARY WARNING ⚠️

    Writing a definition locally does NOT cause execution. This operation
    creates a description file for later platform submission. Platform Core
    controls all execution.

    Example:
        >>> class FileWriter:
        ...     def write(self, content: str, path: Path) -> None:
        ...         # Write content to file
        ...         path.write_text(content)
    """

    def write(self, content: str, path: Path) -> None:
        """
        Write content to persistent storage.

        This method writes the serialized content to the specified location.
        It should handle any necessary encoding, permissions, and error
        handling.

        Args:
            content: The content to write (typically serialized definition).
            path: The destination path for the content.

        Raises:
            IOError: If the write operation fails.
            PermissionError: If write permission is denied.

        Note:
            Writing a definition locally does NOT cause execution.
            Platform Core controls all agent execution.
        """
        ...
