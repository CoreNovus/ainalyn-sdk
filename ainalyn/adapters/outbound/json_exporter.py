"""
JSON Exporter for Agent Manifest (v0.2 AWS MVP Edition).

This module implements JSON serialization for exporting AgentDefinition
to agent.json format, conforming to the v0.2 Agent Manifest Schema.

The output is compatible with 03_agent_manifest_schema.json and includes
SDK-specific extensions as allowed by the specification.

⚠️ SDK BOUNDARY WARNING ⚠️
The exported JSON is a DESCRIPTION for Platform Core submission,
not an executable. Platform Core controls all execution.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.domain.entities import AgentDefinition


class JsonExporter:
    """
    JSON exporter for Agent Manifest format (v0.2).

    This class exports AgentDefinition entities to agent.json format
    conforming to the v0.2 Agent Manifest Schema with SDK extensions.

    The output format follows the structure defined in:
    03_agent_manifest_schema.json

    Key fields per specification:
    - agentId: kebab-case identifier
    - version: semver string
    - type: ATOMIC | COMPOSITE
    - display: name, description, category, icon
    - behavior: isLongRunning, timeoutSeconds
    - inputSchema/outputSchema: JSON Schema
    - pricingStrategy: pricing hint (not billing decision)

    Example:
        >>> from ainalyn.adapters.outbound.json_exporter import JsonExporter
        >>> exporter = JsonExporter()
        >>> json_content = exporter.serialize(agent_definition)
        >>> exporter.write(json_content, Path("agent.json"))
    """

    def serialize(self, definition: AgentDefinition) -> str:
        """
        Export an AgentDefinition to JSON format.

        Args:
            definition: The AgentDefinition to export.

        Returns:
            str: The JSON-formatted string representation.
        """
        data = self.to_manifest_dict(definition)
        return json.dumps(data, indent=2, ensure_ascii=False)

    def to_manifest_dict(self, definition: AgentDefinition) -> dict[str, Any]:
        """
        Convert AgentDefinition to Agent Manifest dictionary.

        This method produces the v0.2 manifest format suitable for
        Platform Core submission.

        Args:
            definition: The AgentDefinition to convert.

        Returns:
            dict[str, Any]: The manifest dictionary.
        """
        result: dict[str, Any] = {
            # Core identification
            "agentId": definition.name,
            "version": definition.version,
            "type": definition.agent_type.value,
        }

        # Display metadata
        if definition.display:
            result["display"] = {
                "name": definition.display.name,
                "description": definition.display.description,
                "category": definition.display.category,
            }
            if definition.display.icon:
                result["display"]["icon"] = definition.display.icon
        else:
            # Fallback to basic fields
            result["display"] = {
                "name": definition.name,
                "description": definition.description,
                "category": "general",
            }

        # Contract completeness (Gate 1)
        if definition.task_goal:
            result["taskGoal"] = definition.task_goal

        if definition.completion_criteria:
            result["completionCriteria"] = {
                "success": definition.completion_criteria.success,
                "failure": definition.completion_criteria.failure,
            }

        # Interface schemas
        result["inputSchema"] = definition.input_schema or {}
        result["outputSchema"] = definition.output_schema or {}
        result["interface"] = {
            "inputSchema": definition.input_schema or {},
            "outputSchema": definition.output_schema or {},
        }

        # Behavior configuration
        if definition.behavior:
            result["behavior"] = {
                "isLongRunning": definition.behavior.is_long_running,
                "timeoutSeconds": definition.behavior.timeout_seconds,
                "idempotent": definition.behavior.idempotent,
                "stateless": definition.behavior.stateless,
            }
        else:
            # Default behavior
            result["behavior"] = {
                "isLongRunning": False,
                "timeoutSeconds": 120,
                "idempotent": True,
                "stateless": True,
            }

        # Pricing strategy (hint only - Gate 4 compliance)
        if definition.pricing_strategy:
            result["pricingStrategy"] = self._pricing_to_dict(
                definition.pricing_strategy
            )

        # Permissions
        if definition.required_permissions:
            result["requiredPermissions"] = list(definition.required_permissions)
        else:
            result["requiredPermissions"] = []

        # EIP dependencies (Gate 5)
        if definition.eip_dependencies:
            result["eipDependencies"] = [
                self._eip_to_dict(dep) for dep in definition.eip_dependencies
            ]

        # Workflow (for COMPOSITE agents)
        from ainalyn.domain.entities.agent_type import AgentType

        if definition.agent_type == AgentType.COMPOSITE and definition.workflows:
            result["workflow"] = self._workflows_to_dict(definition.workflows)

        # SDK extensions (allowed per specification)
        result["_sdk"] = {
            "version": "0.2.0",
            "specVersion": "v0.2-aws-mvp",
        }

        return result

    def write(self, content: str, path: Path) -> None:
        """
        Write JSON content to a file.

        Args:
            content: The JSON content to write.
            path: The destination file path.

        Raises:
            IOError: If the file cannot be written.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _pricing_to_dict(self, pricing: object) -> dict[str, Any]:
        """Convert PricingStrategy to manifest format."""
        from ainalyn.domain.entities import PricingStrategy

        if not isinstance(pricing, PricingStrategy):
            return {}

        result: dict[str, Any] = {
            "type": pricing.type.value,
            "currency": pricing.currency,
        }

        if pricing.fixed_price_cents is not None:
            result["fixedPriceCents"] = pricing.fixed_price_cents

        if pricing.usage_rate_per_unit is not None:
            result["usageRatePerUnit"] = pricing.usage_rate_per_unit

        if pricing.usage_unit:
            result["usageUnit"] = pricing.usage_unit

        if pricing.components:
            result["components"] = [
                {
                    "name": c.name,
                    "type": c.type.value,
                    "amountCents": c.amount_cents,
                    "ratePerUnit": c.rate_per_unit,
                    "unit": c.unit,
                    "includedUnits": c.included_units,
                }
                for c in pricing.components
            ]

        return result

    def _eip_to_dict(self, dep: object) -> dict[str, Any]:
        """Convert EIPDependency to manifest format."""
        from ainalyn.domain.entities import EIPDependency

        if not isinstance(dep, EIPDependency):
            return {}

        result: dict[str, Any] = {
            "provider": dep.provider,
            "service": dep.service,
        }

        if dep.version != "*":
            result["version"] = dep.version

        if dep.config_hints:
            result["configHints"] = dep.config_hints

        return result

    def _workflows_to_dict(self, workflows: tuple[object, ...]) -> dict[str, Any]:
        """Convert workflows to manifest format."""
        from ainalyn.domain.entities import Workflow

        if not workflows:
            return {}

        # For COMPOSITE agents, export all workflows
        result: dict[str, Any] = {"workflows": []}

        for workflow in workflows:
            if not isinstance(workflow, Workflow):
                continue

            workflow_dict: dict[str, Any] = {
                "name": workflow.name,
                "description": workflow.description,
                "entryNode": workflow.entry_node,
                "nodes": [],
            }

            for node in workflow.nodes:
                node_dict: dict[str, Any] = {
                    "name": node.name,
                    "description": node.description,
                    "type": node.node_type.value,
                    "reference": node.reference,
                }

                if node.next_nodes:
                    node_dict["nextNodes"] = list(node.next_nodes)

                if node.inputs:
                    node_dict["inputs"] = list(node.inputs)

                if node.outputs:
                    node_dict["outputs"] = list(node.outputs)

                workflow_dict["nodes"].append(node_dict)

            result["workflows"].append(workflow_dict)

        return result
