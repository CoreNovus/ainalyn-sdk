from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Tool:
    """
    An external tool interface declaration.

    Tool represents the contract for an external capability that can be
    invoked during Agent execution. It defines only the interface (input
    and output schemas), not the implementation.

    The actual tool implementation is provided by Execution Implementation
    Providers (EIP) and invoked by Platform Core. The SDK only describes
    the tool's contract.

    Attributes:
        name: Unique identifier for this Tool within the AgentDefinition.
            Must match pattern [a-z0-9-]+.
        description: Human-readable description of this Tool's capability.
        input_schema: JSON Schema defining the expected input structure.
            Should conform to JSON Schema Draft 2020-12 or compatible.
        output_schema: JSON Schema defining the output structure.
            Should conform to JSON Schema Draft 2020-12 or compatible.

    Example:
        >>> tool = Tool(
        ...     name="file-writer",
        ...     description="Writes content to a file in the workspace",
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "path": {"type": "string"},
        ...             "content": {"type": "string"},
        ...             "encoding": {"type": "string", "default": "utf-8"},
        ...         },
        ...         "required": ["path", "content"],
        ...     },
        ...     output_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "success": {"type": "boolean"},
        ...             "bytes_written": {"type": "integer"},
        ...         },
        ...     },
        ... )
    """

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
