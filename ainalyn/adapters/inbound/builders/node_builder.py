"""
NodeBuilder - Fluent builder for Node entities.

⚠️ SDK BOUNDARY WARNING ⚠️
This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
Building locally does NOT mean the platform will execute it.
All execution authority belongs to Platform Core.
"""

from __future__ import annotations

from typing import Self

from ainalyn.domain.errors import (
    InvalidFormatError,
    MissingFieldError,
)
from ainalyn.domain.entities import Node, NodeType
from ainalyn.domain.rules import DefinitionRules


class NodeBuilder:
    """
    Fluent builder for Node entities.

    This builder provides a convenient API for constructing Node
    instances with validation and clear error messages.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
    Building locally does NOT mean the platform will execute it.
    All execution authority belongs to Platform Core.

    Example:
        >>> node = (
        ...     NodeBuilder("fetch")
        ...     .description("Fetch data from API")
        ...     .uses_module("http-fetcher")
        ...     .outputs("raw_data")
        ...     .next_nodes("process")
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a NodeBuilder with a name.

        Args:
            name: The unique identifier for this Node. Must match [a-z0-9-]+.

        Raises:
            InvalidFormatError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidFormatError(
                "name",
                name,
                "Node name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._node_type: NodeType | None = None
        self._reference: str | None = None
        self._inputs: list[str] = []
        self._outputs: list[str] = []
        self._next_nodes: list[str] = []

    def description(self, desc: str) -> Self:
        """
        Set the description for this Node.

        Args:
            desc: Human-readable description of what this Node does.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def uses_module(self, module_name: str) -> Self:
        """
        Set this Node to reference a Module.

        Args:
            module_name: The name of the Module to reference.

        Returns:
            Self: This builder for method chaining.
        """
        self._node_type = NodeType.MODULE
        self._reference = module_name
        return self

    def uses_prompt(self, prompt_name: str) -> Self:
        """
        Set this Node to reference a Prompt.

        Args:
            prompt_name: The name of the Prompt to reference.

        Returns:
            Self: This builder for method chaining.
        """
        self._node_type = NodeType.PROMPT
        self._reference = prompt_name
        return self

    def uses_tool(self, tool_name: str) -> Self:
        """
        Set this Node to reference a Tool.

        Args:
            tool_name: The name of the Tool to reference.

        Returns:
            Self: This builder for method chaining.
        """
        self._node_type = NodeType.TOOL
        self._reference = tool_name
        return self

    def inputs(self, *input_names: str) -> Self:
        """
        Set the input parameters for this Node.

        Args:
            *input_names: Names of input parameters this Node expects.

        Returns:
            Self: This builder for method chaining.
        """
        self._inputs = list(input_names)
        return self

    def outputs(self, *output_names: str) -> Self:
        """
        Set the output parameters for this Node.

        Args:
            *output_names: Names of output parameters this Node produces.

        Returns:
            Self: This builder for method chaining.
        """
        self._outputs = list(output_names)
        return self

    def next_nodes(self, *node_names: str) -> Self:
        """
        Set the next nodes in the workflow.

        Args:
            *node_names: Names of Nodes that follow this one in the flow.

        Returns:
            Self: This builder for method chaining.
        """
        self._next_nodes = list(node_names)
        return self

    def build(self) -> Node:
        """
        Build and return an immutable Node entity.

        Returns:
            Node: A complete, immutable Node instance.

        Raises:
            MissingFieldError: If required fields are not set.
        """
        if self._description is None:
            raise MissingFieldError("description", "NodeBuilder")
        if self._node_type is None:
            raise MissingFieldError(
                "node_type",
                "NodeBuilder (call uses_module, uses_prompt, or uses_tool)",
            )
        if self._reference is None:
            raise MissingFieldError(
                "reference",
                "NodeBuilder (call uses_module, uses_prompt, or uses_tool)",
            )

        return Node(
            name=self._name,
            description=self._description,
            node_type=self._node_type,
            reference=self._reference,
            inputs=tuple(self._inputs),
            outputs=tuple(self._outputs),
            next_nodes=tuple(self._next_nodes),
        )
