from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Module:
    """
    A reusable capability unit.

    Module represents a self-contained functional component that can be
    referenced by Nodes within a Workflow. It defines the input/output
    contract using JSON Schema, allowing the platform to validate data
    flow between Nodes.

    This is a pure description entity. The actual implementation is
    provided by Execution Implementation Providers (EIP) and executed
    by Platform Core.

    Attributes:
        name: Unique identifier for this Module within the AgentDefinition.
            Must match pattern [a-z0-9-]+.
        description: Human-readable description of this Module's capability.
        input_schema: JSON Schema defining the expected input structure.
            Should conform to JSON Schema Draft 2020-12 or compatible.
        output_schema: JSON Schema defining the output structure.
            Should conform to JSON Schema Draft 2020-12 or compatible.

    Example:
        >>> module = Module(
        ...     name="http-fetcher",
        ...     description="Fetches data from HTTP endpoints",
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "url": {"type": "string", "format": "uri"},
        ...             "method": {"type": "string", "enum": ["GET", "POST"]},
        ...         },
        ...         "required": ["url"],
        ...     },
        ...     output_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "status": {"type": "integer"},
        ...             "body": {"type": "string"},
        ...         },
        ...     },
        ... )
    """

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
