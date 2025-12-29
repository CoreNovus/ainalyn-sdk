"""
WorkflowBuilder - Fluent builder for Workflow entities.

⚠️ SDK BOUNDARY WARNING ⚠️
This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
Building locally does NOT mean the platform will execute it.
All execution authority belongs to Platform Core.
"""

from __future__ import annotations

from typing import Self

from ainalyn.domain.errors import (
    DuplicateError,
    EmptyCollectionError,
    InvalidFormatError,
    MissingFieldError,
)
from ainalyn.domain.entities import Node, Workflow
from ainalyn.domain.rules import DefinitionRules


class WorkflowBuilder:
    """
    Fluent builder for Workflow entities.

    This builder provides a convenient API for constructing Workflow
    instances with validation and clear error messages.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
    Building locally does NOT mean the platform will execute it.
    All execution authority belongs to Platform Core.

    Example:
        >>> workflow = (
        ...     WorkflowBuilder("main")
        ...     .description("Main processing workflow")
        ...     .add_node(
        ...         NodeBuilder("fetch")
        ...         .description("Fetch data")
        ...         .uses_module("http-fetcher")
        ...         .build()
        ...     )
        ...     .entry_node("fetch")
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a WorkflowBuilder with a name.

        Args:
            name: The unique identifier for this Workflow. Must match [a-z0-9-]+.

        Raises:
            InvalidFormatError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidFormatError(
                "name",
                name,
                "Workflow name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._nodes: list[Node] = []
        self._entry_node: str | None = None

    def description(self, desc: str) -> Self:
        """
        Set the description for this Workflow.

        Args:
            desc: Human-readable description of what this Workflow accomplishes.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def add_node(self, node: Node) -> Self:
        """
        Add a Node to this Workflow.

        Args:
            node: The Node to add. Can be created using NodeBuilder.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If a node with this name already exists.
        """
        # Check for duplicate names
        if any(n.name == node.name for n in self._nodes):
            raise DuplicateError("node", node.name, f"workflow '{self._name}'")

        self._nodes.append(node)
        return self

    def nodes(self, *nodes: Node) -> Self:
        """
        Set all nodes for this Workflow at once.

        This is an alternative to calling add_node multiple times.

        Args:
            *nodes: The Nodes to add to this Workflow.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If any nodes have duplicate names.
        """
        # Check for duplicate names
        node_names = [n.name for n in nodes]
        seen = set()
        for name in node_names:
            if name in seen:
                raise DuplicateError("node", name, f"workflow '{self._name}'")
            seen.add(name)

        self._nodes = list(nodes)
        return self

    def entry_node(self, node_name: str) -> Self:
        """
        Set the entry node for this Workflow.

        Args:
            node_name: The name of the starting Node in this Workflow.

        Returns:
            Self: This builder for method chaining.
        """
        self._entry_node = node_name
        return self

    def build(self) -> Workflow:
        """
        Build and return an immutable Workflow entity.

        Returns:
            Workflow: A complete, immutable Workflow instance.

        Raises:
            MissingFieldError: If required fields are not set.
            EmptyCollectionError: If no nodes have been added.
            InvalidFormatError: If entry_node doesn't exist in nodes.
        """
        if self._description is None:
            raise MissingFieldError("description", "WorkflowBuilder")
        if not self._nodes:
            raise EmptyCollectionError("nodes", f"Workflow '{self._name}'")
        if self._entry_node is None:
            raise MissingFieldError("entry_node", "WorkflowBuilder")

        # Validate entry_node exists
        node_names = {n.name for n in self._nodes}
        if self._entry_node not in node_names:
            raise InvalidFormatError(
                "entry_node",
                self._entry_node,
                f"Entry node '{self._entry_node}' does not exist in workflow. "
                f"Available nodes: {', '.join(sorted(node_names))}",
            )

        return Workflow(
            name=self._name,
            description=self._description,
            nodes=tuple(self._nodes),
            entry_node=self._entry_node,
        )
