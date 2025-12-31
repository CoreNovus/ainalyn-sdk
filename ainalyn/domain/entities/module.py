from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ainalyn.domain.entities.eip_dependency import EIPBinding


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
        eip_binding: Optional binding to a specific EIP provider and service.
            When specified, Platform Core will route this Module's execution
            to the designated EIP. This is a declaration, not execution.

    Example:
        >>> from ainalyn.domain.entities.eip_dependency import EIPBinding
        >>> module = Module(
        ...     name="audio-transcriber",
        ...     description="Transcribes audio to text with timestamps",
        ...     eip_binding=EIPBinding(provider="openai", service="whisper"),
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "audio_url": {"type": "string", "format": "uri"},
        ...             "language": {"type": "string", "default": "auto"},
        ...         },
        ...         "required": ["audio_url"],
        ...     },
        ...     output_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "transcript": {"type": "string"},
        ...             "segments": {"type": "array"},
        ...         },
        ...     },
        ... )
    """

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    eip_binding: EIPBinding | None = None
