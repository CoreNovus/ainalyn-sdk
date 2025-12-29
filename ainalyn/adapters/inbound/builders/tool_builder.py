"""
ToolBuilder - Fluent builder for Tool entities.

⚠️ SDK BOUNDARY WARNING ⚠️
This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
Building locally does NOT mean the platform will execute it.
All execution authority belongs to Platform Core.
"""

from __future__ import annotations

from typing import Any, Self

from ainalyn.domain.errors import (
    InvalidFormatError,
    MissingFieldError,
)
from ainalyn.domain.entities import Tool
from ainalyn.domain.rules import DefinitionRules


class ToolBuilder:
    """
    Fluent builder for Tool entities.

    This builder provides a convenient API for constructing Tool
    instances with validation and clear error messages.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
    Building locally does NOT mean the platform will execute it.
    All execution authority belongs to Platform Core.

    Example:
        >>> tool = (
        ...     ToolBuilder("file-writer")
        ...     .description("Writes content to a file")
        ...     .input_schema({
        ...         "type": "object",
        ...         "properties": {"path": {"type": "string"}},
        ...     })
        ...     .output_schema({
        ...         "type": "object",
        ...         "properties": {"success": {"type": "boolean"}},
        ...     })
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a ToolBuilder with a name.

        Args:
            name: The unique identifier for this Tool. Must match [a-z0-9-]+.

        Raises:
            InvalidFormatError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidFormatError(
                "name",
                name,
                "Tool name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._input_schema: dict[str, Any] = {}
        self._output_schema: dict[str, Any] = {}

    def description(self, desc: str) -> Self:
        """
        Set the description for this Tool.

        Args:
            desc: Human-readable description of this Tool's capability.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def input_schema(self, schema: dict[str, Any]) -> Self:
        """
        Set the input JSON Schema for this Tool.

        Args:
            schema: JSON Schema defining the expected input structure.

        Returns:
            Self: This builder for method chaining.
        """
        self._input_schema = schema
        return self

    def output_schema(self, schema: dict[str, Any]) -> Self:
        """
        Set the output JSON Schema for this Tool.

        Args:
            schema: JSON Schema defining the output structure.

        Returns:
            Self: This builder for method chaining.
        """
        self._output_schema = schema
        return self

    def build(self) -> Tool:
        """
        Build and return an immutable Tool entity.

        Returns:
            Tool: A complete, immutable Tool instance.

        Raises:
            MissingFieldError: If description is not set.
        """
        if self._description is None:
            raise MissingFieldError("description", "ToolBuilder")

        return Tool(
            name=self._name,
            description=self._description,
            input_schema=self._input_schema,
            output_schema=self._output_schema,
        )
