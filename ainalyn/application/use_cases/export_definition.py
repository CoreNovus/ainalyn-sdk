"""
Use case for exporting Agent Definitions.

This module implements the export use case that converts
AgentDefinition entities to YAML format.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.adapters.secondary.exporters import YamlExporter
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
        >>> from ainalyn.adapters.secondary import YamlExporter
        >>> from ainalyn.application.use_cases import ExportDefinitionUseCase
        >>> from pathlib import Path
        >>> exporter = YamlExporter()
        >>> use_case = ExportDefinitionUseCase(exporter)
        >>> # Export to string
        >>> yaml_content = use_case.execute(agent_definition)
        >>> # Export to file
        >>> use_case.execute_to_file(agent_definition, Path("agent.yaml"))
    """

    def __init__(self, exporter: YamlExporter) -> None:
        """
        Initialize the export use case.

        Args:
            exporter: The YAML exporter to use for serialization.
        """
        self._exporter = exporter

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
        return self._exporter.export(definition)

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
        yaml_content = self._exporter.export(definition)
        self._exporter.write(yaml_content, path)
