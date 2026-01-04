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
        Export an AgentDefinition to YAML format (alias for serialize).

        This method is an alias for serialize() to maintain backward
        compatibility with existing code and tests.

        Args:
            definition: The AgentDefinition to export.

        Returns:
            str: The YAML-formatted string representation with header comments.

        Note:
            This is an alias for serialize(). Both methods are equivalent.
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

        v0.2 AWS MVP Edition: Now includes agent_type, display, behavior,
        pricing_strategy, input_schema, output_schema, and required_permissions.

        Args:
            definition: The AgentDefinition to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        result: dict[str, Any] = {
            "name": definition.name,
            "version": definition.version,
            "description": definition.description,
            "agent_type": definition.agent_type.value,
        }

        # v0.2: Add display metadata
        if definition.display:
            result["display"] = self._display_to_dict(definition.display)

        # Add task_goal if present (Review Gate 1 requirement)
        if definition.task_goal:
            result["task_goal"] = definition.task_goal

        # Add completion_criteria if present (Review Gate 1 requirement)
        if definition.completion_criteria:
            result["completion_criteria"] = self._completion_criteria_to_dict(
                definition.completion_criteria
            )

        # v0.2: Add schemas
        if definition.input_schema:
            result["input_schema"] = definition.input_schema

        if definition.output_schema:
            result["output_schema"] = definition.output_schema

        # v0.2: Add behavior
        if definition.behavior:
            result["behavior"] = self._behavior_to_dict(definition.behavior)

        # v0.2: Add pricing strategy
        if definition.pricing_strategy:
            result["pricing_strategy"] = self._pricing_strategy_to_dict(
                definition.pricing_strategy
            )

        # v0.2: Add required permissions
        if definition.required_permissions:
            result["required_permissions"] = list(definition.required_permissions)

        # Add EIP dependencies if present (Review Gate 5 requirement)
        if definition.eip_dependencies:
            result["eip_dependencies"] = [
                self._eip_dependency_to_dict(dep) for dep in definition.eip_dependencies
            ]

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

        # Add EIP binding if present
        if module.eip_binding:
            result["eip_binding"] = self._eip_binding_to_dict(module.eip_binding)

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

        # Add EIP binding if present
        if tool.eip_binding:
            result["eip_binding"] = self._eip_binding_to_dict(tool.eip_binding)

        # Add schemas if present
        if tool.input_schema:
            result["input_schema"] = tool.input_schema

        if tool.output_schema:
            result["output_schema"] = tool.output_schema

        return result

    def _eip_binding_to_dict(self, binding: object) -> dict[str, Any]:
        """
        Convert EIPBinding to dictionary representation.

        Args:
            binding: The EIPBinding to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import EIPBinding

        if not isinstance(binding, EIPBinding):
            return {}

        return {
            "provider": binding.provider,
            "service": binding.service,
        }

    def _eip_dependency_to_dict(self, dependency: object) -> dict[str, Any]:
        """
        Convert EIPDependency to dictionary representation.

        Args:
            dependency: The EIPDependency to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import EIPDependency

        if not isinstance(dependency, EIPDependency):
            return {}

        result: dict[str, Any] = {
            "provider": dependency.provider,
            "service": dependency.service,
        }

        if dependency.version != "*":
            result["version"] = dependency.version

        if dependency.config_hints:
            result["config_hints"] = dependency.config_hints

        return result

    def _completion_criteria_to_dict(self, criteria: object) -> dict[str, Any]:
        """
        Convert CompletionCriteria to dictionary representation.

        Args:
            criteria: The CompletionCriteria to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import CompletionCriteria

        if not isinstance(criteria, CompletionCriteria):
            return {}

        return {
            "success": criteria.success,
            "failure": criteria.failure,
        }

    # ========== v0.2 Conversion Methods ==========

    def _display_to_dict(self, display: object) -> dict[str, Any]:
        """
        Convert DisplayInfo to dictionary representation (v0.2).

        Args:
            display: The DisplayInfo to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import DisplayInfo

        if not isinstance(display, DisplayInfo):
            return {}

        result: dict[str, Any] = {
            "name": display.name,
            "description": display.description,
            "category": display.category,
        }

        if display.icon:
            result["icon"] = display.icon

        return result

    def _behavior_to_dict(self, behavior: object) -> dict[str, Any]:
        """
        Convert BehaviorConfig to dictionary representation (v0.2).

        Args:
            behavior: The BehaviorConfig to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import BehaviorConfig

        if not isinstance(behavior, BehaviorConfig):
            return {}

        return {
            "is_long_running": behavior.is_long_running,
            "timeout_seconds": behavior.timeout_seconds,
            "idempotent": behavior.idempotent,
            "stateless": behavior.stateless,
        }

    def _pricing_strategy_to_dict(self, pricing: object) -> dict[str, Any]:
        """
        Convert PricingStrategy to dictionary representation (v0.2).

        IMPORTANT: This is a DESCRIPTION only. SDK does NOT calculate fees.

        Args:
            pricing: The PricingStrategy to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import PricingStrategy

        if not isinstance(pricing, PricingStrategy):
            return {}

        result: dict[str, Any] = {
            "type": pricing.type.value,
            "currency": pricing.currency,
        }

        if pricing.fixed_price_cents is not None:
            result["fixed_price_cents"] = pricing.fixed_price_cents

        if pricing.usage_rate_per_unit is not None:
            result["usage_rate_per_unit"] = pricing.usage_rate_per_unit

        if pricing.usage_unit:
            result["usage_unit"] = pricing.usage_unit

        if pricing.components:
            result["components"] = [
                self._pricing_component_to_dict(c) for c in pricing.components
            ]

        return result

    def _pricing_component_to_dict(self, component: object) -> dict[str, Any]:
        """
        Convert PricingComponent to dictionary representation (v0.2).

        Args:
            component: The PricingComponent to convert.

        Returns:
            dict[str, Any]: The dictionary representation.
        """
        from ainalyn.domain.entities import PricingComponent

        if not isinstance(component, PricingComponent):
            return {}

        result: dict[str, Any] = {
            "name": component.name,
            "type": component.type.value,
        }

        if component.amount_cents is not None:
            result["amount_cents"] = component.amount_cents

        if component.rate_per_unit is not None:
            result["rate_per_unit"] = component.rate_per_unit

        if component.unit:
            result["unit"] = component.unit

        if component.included_units is not None:
            result["included_units"] = component.included_units

        return result
