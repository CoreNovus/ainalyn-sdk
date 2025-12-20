"""
Domain rules for Agent Definition validation.

This module contains pure domain logic for validating the consistency
and correctness of AgentDefinition entities. These rules are part of
the domain layer and do not depend on any external systems.

The rules defined here are used by validators in the application layer
to ensure AgentDefinitions conform to platform requirements.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition, Workflow

# Pattern for valid names: lowercase letters, numbers, and hyphens
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")

# Pattern for semantic versioning (simplified)
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?$")


class DefinitionRules:
    """
    Domain rules for validating AgentDefinition entities.

    This class provides static methods that encapsulate the core
    business rules for Agent Definitions. These rules are:

    1. Pure functions with no side effects
    2. Independent of external systems (no I/O, no network)
    3. Deterministic (same input always produces same output)

    These rules form the foundation for validation but do not
    generate user-facing error messages. That responsibility
    belongs to the validation adapters.

    Example:
        >>> from ainalyn.domain.rules import DefinitionRules
        >>> DefinitionRules.is_valid_name("my-agent")
        True
        >>> DefinitionRules.is_valid_name("My Agent")
        False
    """

    @staticmethod
    def is_valid_name(name: str) -> bool:
        """
        Check if a name follows the naming convention.

        Valid names must:
        - Start with a lowercase letter
        - Contain only lowercase letters, numbers, and hyphens
        - Not be empty

        Args:
            name: The name to validate.

        Returns:
            bool: True if the name is valid, False otherwise.

        Example:
            >>> DefinitionRules.is_valid_name("data-processor")
            True
            >>> DefinitionRules.is_valid_name("DataProcessor")
            False
        """
        if not name:
            return False
        return NAME_PATTERN.match(name) is not None

    @staticmethod
    def is_valid_version(version: str) -> bool:
        """
        Check if a version string follows semantic versioning.

        Valid versions must follow the pattern: MAJOR.MINOR.PATCH
        Optional pre-release and build metadata are allowed.

        Args:
            version: The version string to validate.

        Returns:
            bool: True if the version is valid, False otherwise.

        Example:
            >>> DefinitionRules.is_valid_version("1.0.0")
            True
            >>> DefinitionRules.is_valid_version("1.0.0-alpha.1")
            True
            >>> DefinitionRules.is_valid_version("v1.0")
            False
        """
        if not version:
            return False
        return SEMVER_PATTERN.match(version) is not None

    @staticmethod
    def workflow_has_valid_entry(workflow: Workflow) -> bool:
        """
        Check if a Workflow's entry_node exists in its nodes.

        The entry_node must reference a Node that is defined
        within the Workflow's nodes tuple.

        Args:
            workflow: The Workflow to validate.

        Returns:
            bool: True if the entry_node exists, False otherwise.
        """
        if not workflow.entry_node:
            return False
        node_names = {node.name for node in workflow.nodes}
        return workflow.entry_node in node_names

    @staticmethod
    def workflow_has_nodes(workflow: Workflow) -> bool:
        """
        Check if a Workflow has at least one Node.

        An empty Workflow is not valid as it cannot perform any task.

        Args:
            workflow: The Workflow to validate.

        Returns:
            bool: True if the Workflow has nodes, False otherwise.
        """
        return len(workflow.nodes) > 0

    @staticmethod
    def get_undefined_node_references(workflow: Workflow) -> list[tuple[str, str]]:
        """
        Find Nodes that reference non-existent next_nodes.

        This method checks each Node's next_nodes to ensure they
        reference Nodes that exist within the Workflow.

        Args:
            workflow: The Workflow to check.

        Returns:
            list[tuple[str, str]]: List of (source_node, undefined_reference)
                pairs for each undefined reference found.

        Example:
            >>> # If node "a" references next_node "b" but "b" doesn't exist
            >>> DefinitionRules.get_undefined_node_references(workflow)
            [("a", "b")]
        """
        node_names = {node.name for node in workflow.nodes}
        undefined: list[tuple[str, str]] = []

        for node in workflow.nodes:
            undefined.extend(
                (node.name, next_node)
                for next_node in node.next_nodes
                if next_node not in node_names
            )

        return undefined

    @staticmethod
    def get_undefined_resource_references(
        definition: AgentDefinition,
    ) -> list[tuple[str, str, str]]:
        """
        Find Nodes that reference non-existent modules, prompts, or tools.

        This method checks each Node's reference to ensure it points
        to a resource that exists in the AgentDefinition.

        Args:
            definition: The AgentDefinition to check.

        Returns:
            list[tuple[str, str, str]]: List of (node_name, resource_type, reference)
                tuples for each undefined reference found.

        Example:
            >>> # If node references module "foo" but it's not defined
            >>> DefinitionRules.get_undefined_resource_references(definition)
            [("fetch", "module", "foo")]
        """
        module_names = {m.name for m in definition.modules}
        prompt_names = {p.name for p in definition.prompts}
        tool_names = {t.name for t in definition.tools}

        resource_sets = {
            "module": module_names,
            "prompt": prompt_names,
            "tool": tool_names,
        }

        undefined: list[tuple[str, str, str]] = []

        for workflow in definition.workflows:
            for node in workflow.nodes:
                resource_type = node.node_type.value
                reference = node.reference
                resource_set = resource_sets.get(resource_type, set())

                if reference not in resource_set:
                    undefined.append((node.name, resource_type, reference))

        return undefined

    @staticmethod
    def detect_circular_dependencies(workflow: Workflow) -> list[list[str]]:
        """
        Detect circular dependencies in a Workflow's node graph.

        This method uses depth-first search to find cycles in the
        directed graph formed by Nodes and their next_nodes.

        Args:
            workflow: The Workflow to analyze.

        Returns:
            list[list[str]]: List of cycles found, where each cycle
                is a list of Node names forming the cycle.

        Example:
            >>> # If a -> b -> c -> a
            >>> DefinitionRules.detect_circular_dependencies(workflow)
            [["a", "b", "c", "a"]]
        """
        # Build adjacency list
        graph: dict[str, list[str]] = {}
        for node in workflow.nodes:
            graph[node.name] = list(node.next_nodes)

        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node_name: str) -> None:
            if node_name not in graph:
                return

            visited.add(node_name)
            rec_stack.add(node_name)
            path.append(node_name)

            for next_node in graph.get(node_name, []):
                if next_node not in visited:
                    dfs(next_node)
                elif next_node in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(next_node)
                    cycle = [*path[cycle_start:], next_node]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node_name)

        for node_name in graph:
            if node_name not in visited:
                dfs(node_name)

        return cycles

    @staticmethod
    def get_unreachable_nodes(workflow: Workflow) -> list[str]:
        """
        Find Nodes that are not reachable from the entry_node.

        This method performs a breadth-first traversal from the
        entry_node to find all reachable Nodes, then returns
        any Nodes that were not reached.

        Args:
            workflow: The Workflow to analyze.

        Returns:
            list[str]: Names of Nodes that cannot be reached from
                the entry_node.

        Example:
            >>> # If entry is "a" -> "b", but "c" exists with no incoming edges
            >>> DefinitionRules.get_unreachable_nodes(workflow)
            ["c"]
        """
        if not workflow.nodes or not workflow.entry_node:
            return []

        all_nodes = {node.name for node in workflow.nodes}

        # Build adjacency list
        graph: dict[str, list[str]] = {}
        for node in workflow.nodes:
            graph[node.name] = list(node.next_nodes)

        # BFS from entry_node
        reachable: set[str] = set()
        queue = [workflow.entry_node]

        while queue:
            current = queue.pop(0)
            if current in reachable or current not in all_nodes:
                continue
            reachable.add(current)
            queue.extend(graph.get(current, []))

        unreachable = all_nodes - reachable
        return sorted(unreachable)

    @staticmethod
    def get_unused_resources(
        definition: AgentDefinition,
    ) -> dict[str, list[str]]:
        """
        Find modules, prompts, and tools that are defined but never used.

        This method identifies resources that are declared in the
        AgentDefinition but not referenced by any Node.

        Args:
            definition: The AgentDefinition to analyze.

        Returns:
            dict[str, list[str]]: Dictionary with keys "modules", "prompts",
                and "tools", each containing a list of unused resource names.

        Example:
            >>> result = DefinitionRules.get_unused_resources(definition)
            >>> result["modules"]
            ["unused-module"]
        """
        # Collect all references from nodes
        referenced_modules: set[str] = set()
        referenced_prompts: set[str] = set()
        referenced_tools: set[str] = set()

        for workflow in definition.workflows:
            for node in workflow.nodes:
                if node.node_type.value == "module":
                    referenced_modules.add(node.reference)
                elif node.node_type.value == "prompt":
                    referenced_prompts.add(node.reference)
                elif node.node_type.value == "tool":
                    referenced_tools.add(node.reference)

        # Find unused resources
        defined_modules = {m.name for m in definition.modules}
        defined_prompts = {p.name for p in definition.prompts}
        defined_tools = {t.name for t in definition.tools}

        return {
            "modules": sorted(defined_modules - referenced_modules),
            "prompts": sorted(defined_prompts - referenced_prompts),
            "tools": sorted(defined_tools - referenced_tools),
        }
