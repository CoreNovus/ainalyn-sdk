"""
Use case for exporting Agent Definitions.

This module implements the export use case that converts
AgentDefinition entities to YAML format.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.application.ports.outbound.definition_serialization import (
        IDefinitionSerializer,
    )
    from ainalyn.domain.entities import AgentDefinition


class ExportDefinitionUseCase:
    """
    Use case for exporting Agent Definitions to YAML.

    This use case orchestrates the export process by:
    1. Converting AgentDefinition to YAML format
    2. Optionally writing to a file

    The use case provides both in-memory export (for testing or
    programmatic use) and file export (for platform submission).

    Example:
        >>> from ainalyn.adapters.outbound import YamlExporter
        >>> from ainalyn.application.use_cases import ExportDefinitionUseCase
        >>> from pathlib import Path
        >>> exporter = YamlExporter()
        >>> use_case = ExportDefinitionUseCase(exporter)
        >>> # Export to string
        >>> yaml_content = use_case.execute(agent_definition)
        >>> # Export to file
        >>> use_case.execute_to_file(agent_definition, Path("agent.yaml"))
    """

    def __init__(self, serializer: IDefinitionSerializer) -> None:
        """
        Initialize the export use case.

        Args:
            serializer: The serializer to use for converting to YAML format.
        """
        self._serializer = serializer

    def execute(self, definition: AgentDefinition) -> str:
        """
        Export an AgentDefinition to YAML string.

        This method converts the AgentDefinition into a YAML-formatted
        string representation suitable for platform submission.

        Args:
            definition: The AgentDefinition to export.

        Returns:
            str: The YAML-formatted string representation.

        Raises:
            yaml.YAMLError: If YAML serialization fails.
        """
        return self._serializer.serialize(definition)

    def execute_to_file(self, definition: AgentDefinition, path: Path) -> None:
        """
        Export an AgentDefinition to a YAML file.

        This method converts the AgentDefinition to YAML and writes
        it to the specified file path. Parent directories are created
        automatically if they do not exist.

        Args:
            definition: The AgentDefinition to export.
            path: The destination file path.

        Raises:
            yaml.YAMLError: If YAML serialization fails.
            IOError: If the file cannot be written.
            PermissionError: If write permission is denied.
        """
        yaml_content = self._serializer.serialize(definition)
        # Write to file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml_content, encoding="utf-8")
