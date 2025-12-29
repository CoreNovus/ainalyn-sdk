"""
YAML serializer for Agent Definitions.

This module implements YAML serialization as an outbound adapter,
converting AgentDefinition entities to YAML format for platform submission.
It implements the IDefinitionSerializer port interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.domain.entities import AgentDefinition


class YamlExporter:
    """
    YAML serializer for AgentDefinition entities.

    This class implements the IDefinitionSerializer outbound port,
    converting AgentDefinition entities to YAML format.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    The serialized YAML is a DESCRIPTION for platform submission,
    not an executable. Platform Core controls all execution.

    The YAML output follows a specific structure suitable for
    platform submission, with keys ordered for readability.

    Features:
    - Full Unicode support for international content
    - Deterministic key ordering
    - Human-readable formatting
    - Platform boundary warnings in header

    Example:
        >>> from ainalyn.adapters.outbound.yaml_serializer import YamlExporter
        >>> from ainalyn.domain.entities import AgentDefinition
        >>> exporter = YamlExporter()
        >>> yaml_content = exporter.serialize(agent_definition)
    """

    # YAML header comment with platform boundary warning
    _YAML_HEADER = """# Ainalyn Agent Definition
# This file is a DESCRIPTION submitted to Platform Core for review.
# It does NOT execute by itself. Execution is handled exclusively by Platform Core.
#
# ⚠️  CRITICAL BOUNDARY WARNING ⚠️
# - SDK validation passed ≠ Platform will execute this definition
# - Platform performs additional governance, security, and resource checks
# - Platform Core has sole authority over execution, billing, and lifecycle
#
# Local compilation does NOT equal platform execution.
# See: https://docs.ainalyn.io/sdk/platform-boundaries/

"""

    def serialize(self, definition: AgentDefinition) -> str:
        """
        Export an AgentDefinition to YAML format.

        This method converts the AgentDefinition into a YAML string
        representation suitable for platform submission.

        Args:
            definition: The AgentDefinition to export.

        Returns:
            str: The YAML-formatted string representation with header comments.

        Raises:
            yaml.YAMLError: If YAML serialization fails.
        """
        # Convert to dictionary representation
        data = self._to_dict(definition)

        # Serialize to YAML with Unicode support and readable formatting
        yaml_content = yaml.dump(
            data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
        )
        assert isinstance(yaml_content, str)  # yaml.dump returns str

        # Prepend header comment to explain the file's purpose
        return self._YAML_HEADER + yaml_content

    def export(self, definition: AgentDefinition) -> str:
        """
        Export an AgentDefinition to YAML format (legacy alias).

        This method is an alias for serialize() to maintain backward
        compatibility. New code should use serialize() instead.

        Args:
            definition: The AgentDefinition to export.

        Returns:
            str: The YAML-formatted string representation with header comments.

        Deprecated:
            Use serialize() instead. This method will be removed in a future version.
        """
        return self.serialize(definition)

    def write(self, content: str, path: Path) -> None:
        """
        Write YAML content to a file.

        This method persists the given YAML content to the specified
        file path. Parent directories are created automatically if they
        do not exist.

        Args:
            content: The YAML content to write.
            path: The destination file path.

        Raises:
            IOError: If the file cannot be written.
            PermissionError: If write permission is denied.
        """
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write content with UTF-8 encoding
        path.write_text(content, encoding="utf-8")

    def _to_dict(self, definition: AgentDefinition) -> dict[str, Any]:
        """
        Convert AgentDefinition to dictionary representation.

        This method transforms the AgentDefinition into a structured
        dictionary suitable for YAML serialization. Keys are ordered
        for readability.

        Args:
            definition: The AgentDefinition to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        result: dict[str, Any] = {
            "name": definition.name,
            "version": definition.version,
            "description": definition.description,
        }

        # Add workflows
        if definition.workflows:
            result["workflows"] = [
                self._workflow_to_dict(workflow) for workflow in definition.workflows
            ]

        # Add modules if present
        if definition.modules:
            result["modules"] = [
                self._module_to_dict(module) for module in definition.modules
            ]

        # Add prompts if present
        if definition.prompts:
            result["prompts"] = [
                self._prompt_to_dict(prompt) for prompt in definition.prompts
            ]

        # Add tools if present
        if definition.tools:
            result["tools"] = [self._tool_to_dict(tool) for tool in definition.tools]

        return result

    def _workflow_to_dict(self, workflow: object) -> dict[str, Any]:
        """
        Convert Workflow to dictionary representation.

        Args:
            workflow: The Workflow to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import Workflow

        if not isinstance(workflow, Workflow):
            return {}

        result: dict[str, Any] = {
            "name": workflow.name,
            "description": workflow.description,
            "entry_node": workflow.entry_node,
        }

        # Add nodes
        if workflow.nodes:
            result["nodes"] = [self._node_to_dict(node) for node in workflow.nodes]

        return result

    def _node_to_dict(self, node: object) -> dict[str, Any]:
        """
        Convert Node to dictionary representation.

        Args:
            node: The Node to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import Node

        if not isinstance(node, Node):
            return {}

        result: dict[str, Any] = {
            "name": node.name,
            "description": node.description,
            "type": node.node_type.value,
            "reference": node.reference,
        }

        # Add optional fields if present
        if node.next_nodes:
            result["next_nodes"] = list(node.next_nodes)

        if node.inputs:
            result["inputs"] = list(node.inputs)

        if node.outputs:
            result["outputs"] = list(node.outputs)

        return result

    def _module_to_dict(self, module: object) -> dict[str, Any]:
        """
        Convert Module to dictionary representation.

        Args:
            module: The Module to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import Module

        if not isinstance(module, Module):
            return {}

        result: dict[str, Any] = {
            "name": module.name,
            "description": module.description,
        }

        # Add schemas if present
        if module.input_schema:
            result["input_schema"] = module.input_schema

        if module.output_schema:
            result["output_schema"] = module.output_schema

        return result

    def _prompt_to_dict(self, prompt: object) -> dict[str, Any]:
        """
        Convert Prompt to dictionary representation.

        Args:
            prompt: The Prompt to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import Prompt

        if not isinstance(prompt, Prompt):
            return {}

        result: dict[str, Any] = {
            "name": prompt.name,
            "description": prompt.description,
            "template": prompt.template,
        }

        # Add variables if present
        if prompt.variables:
            result["variables"] = list(prompt.variables)

        return result

    def _tool_to_dict(self, tool: object) -> dict[str, Any]:
        """
        Convert Tool to dictionary representation.

        Args:
            tool: The Tool to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import Tool

        if not isinstance(tool, Tool):
            return {}

        result: dict[str, Any] = {
            "name": tool.name,
            "description": tool.description,
        }

        # Add schemas if present
        if tool.input_schema:
            result["input_schema"] = tool.input_schema

        if tool.output_schema:
            result["output_schema"] = tool.output_schema

        return result
