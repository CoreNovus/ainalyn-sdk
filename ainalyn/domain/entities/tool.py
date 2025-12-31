from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ainalyn.domain.entities.eip_dependency import EIPBinding


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
        eip_binding: Optional binding to a specific EIP provider and service.
            When specified, Platform Core will route this Tool's execution
            to the designated EIP. This is a declaration, not execution.

    Example:
        >>> from ainalyn.domain.entities.eip_dependency import EIPBinding
        >>> tool = Tool(
        ...     name="speech-to-text",
        ...     description="Converts audio to text using speech recognition",
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
