"""
Static analyzer for Agent Definitions.

This module implements static analysis as an outbound adapter,
performing logical consistency checks on AgentDefinition entities.
It implements the IDefinitionAnalyzer port interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.application.ports.inbound.validate_agent_definition import (
    Severity,
    ValidationError,
)
from ainalyn.domain.rules import DefinitionRules

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition


class StaticAnalyzer:
    """
    Static analyzer for AgentDefinition entities.

    This class implements the IDefinitionAnalyzer outbound port,
    performing logical consistency checks and detecting potential
    issues in Agent Definitions.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    This analysis checks SDK-level logical correctness only.
    Platform Core applies additional checks during submission.

    The analyzer checks:
    - Circular dependencies in workflows
    - Unreachable nodes
    - Unused resources (modules, prompts, tools)
    - Dead-end nodes (nodes with no next_nodes and no outputs)

    Unlike SchemaValidator which checks structural correctness,
    StaticAnalyzer checks logical consistency and code quality.

    Example:
        >>> from ainalyn.adapters.outbound.static_analyzer import StaticAnalyzer
        >>> analyzer = StaticAnalyzer()
        >>> warnings = analyzer.analyze(agent_definition)
        >>> for warning in warnings:
        ...     print(f"{warning.code}: {warning.message}")
    """

    def analyze(self, definition: AgentDefinition) -> tuple[ValidationError, ...]:
        """
        Analyze an AgentDefinition for logical issues.

        This method performs comprehensive static analysis including:
        - Circular dependency detection
        - Unreachable node detection
        - Unused resource detection
        - Dead-end node detection

        Args:
            definition: The AgentDefinition to analyze.

        Returns:
            tuple[ValidationError, ...]: Tuple of warnings and errors found.
                Most issues are warnings (Severity.WARNING) unless they
                indicate critical logical errors.
        """
        issues: list[ValidationError] = []

        # Detect circular dependencies
        issues.extend(self._detect_circular_dependencies(definition))

        # Detect unreachable nodes
        issues.extend(self._detect_unreachable_nodes(definition))

        # Detect unused resources
        issues.extend(self._detect_unused_resources(definition))

        # Detect dead-end nodes
        issues.extend(self._detect_dead_end_nodes(definition))

        return tuple(issues)

    def _detect_circular_dependencies(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Detect circular dependencies in workflows."""
        issues: list[ValidationError] = []

        for wf_idx, workflow in enumerate(definition.workflows):
            cycles = DefinitionRules.detect_circular_dependencies(workflow)

            for cycle in cycles:
                # Format the cycle path
                cycle_path = " -> ".join(cycle)

                issues.append(
                    ValidationError(
                        code="CIRCULAR_DEPENDENCY",
                        path=f"agent.workflows[{wf_idx}]",
                        message=(
                            f"Circular dependency detected in workflow "
                            f"'{workflow.name}': {cycle_path}"
                        ),
                        severity=Severity.ERROR,
                    )
                )

        return issues

    def _detect_unreachable_nodes(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Detect nodes that cannot be reached from entry_node."""
        issues: list[ValidationError] = []

        for wf_idx, workflow in enumerate(definition.workflows):
            unreachable = DefinitionRules.get_unreachable_nodes(workflow)

            for node_name in unreachable:
                # Find the node index
                for node_idx, node in enumerate(workflow.nodes):
                    if node.name == node_name:
                        issues.append(
                            ValidationError(
                                code="UNREACHABLE_NODE",
                                path=(
                                    f"agent.workflows[{wf_idx}].nodes[{node_idx}]"
                                ),
                                message=(
                                    f"Node '{node_name}' is unreachable from "
                                    f"entry node '{workflow.entry_node}' in "
                                    f"workflow '{workflow.name}'"
                                ),
                                severity=Severity.WARNING,
                            )
                        )
                        break

        return issues

    def _detect_unused_resources(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Detect resources that are defined but never used."""
        issues: list[ValidationError] = []

        unused = DefinitionRules.get_unused_resources(definition)

        # Report unused modules
        for module_name in unused["modules"]:
            # Find the module index
            for idx, module in enumerate(definition.modules):
                if module.name == module_name:
                    issues.append(
                        ValidationError(
                            code="UNUSED_MODULE",
                            path=f"agent.modules[{idx}]",
                            message=(
                                f"Module '{module_name}' is defined but never "
                                "referenced by any node"
                            ),
                            severity=Severity.WARNING,
                        )
                    )
                    break

        # Report unused prompts
        for prompt_name in unused["prompts"]:
            # Find the prompt index
            for idx, prompt in enumerate(definition.prompts):
                if prompt.name == prompt_name:
                    issues.append(
                        ValidationError(
                            code="UNUSED_PROMPT",
                            path=f"agent.prompts[{idx}]",
                            message=(
                                f"Prompt '{prompt_name}' is defined but never "
                                "referenced by any node"
                            ),
                            severity=Severity.WARNING,
                        )
                    )
                    break

        # Report unused tools
        for tool_name in unused["tools"]:
            # Find the tool index
            for idx, tool in enumerate(definition.tools):
                if tool.name == tool_name:
                    issues.append(
                        ValidationError(
                            code="UNUSED_TOOL",
                            path=f"agent.tools[{idx}]",
                            message=(
                                f"Tool '{tool_name}' is defined but never "
                                "referenced by any node"
                            ),
                            severity=Severity.WARNING,
                        )
                    )
                    break

        return issues

    def _detect_dead_end_nodes(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Detect nodes that may be dead-ends (no next_nodes and no outputs)."""
        issues: list[ValidationError] = []

        for wf_idx, workflow in enumerate(definition.workflows):
            for node_idx, node in enumerate(workflow.nodes):
                # A node is potentially a dead-end if:
                # 1. It has no next_nodes (terminal node)
                # 2. It has no outputs
                # This might indicate the node doesn't contribute to the workflow
                if not node.next_nodes and not node.outputs:
                    issues.append(
                        ValidationError(
                            code="POTENTIAL_DEAD_END",
                            path=f"agent.workflows[{wf_idx}].nodes[{node_idx}]",
                            message=(
                                f"Node '{node.name}' has no next nodes and no "
                                f"outputs. This might indicate a dead-end or "
                                f"incomplete workflow in '{workflow.name}'"
                            ),
                            severity=Severity.WARNING,
                        )
                    )

        return issues
