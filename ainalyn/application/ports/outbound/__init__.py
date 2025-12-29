"""
Outbound ports for Ainalyn SDK.

Outbound ports define the capabilities that the application core needs
from the external world. They represent "what the application needs"
rather than "how it's implemented".

Examples of outbound ports:
- Schema validation capability
- Static analysis capability
- Serialization capability
- Persistence capability

These ports are implemented by outbound adapters (secondary adapters).
"""

from __future__ import annotations

from ainalyn.application.ports.outbound.definition_persistence import (
    IDefinitionWriter,
)
from ainalyn.application.ports.outbound.definition_schema_validation import (
    IDefinitionSchemaValidator,
)
from ainalyn.application.ports.outbound.definition_serialization import (
    IDefinitionSerializer,
)
from ainalyn.application.ports.outbound.definition_static_analysis import (
    IDefinitionAnalyzer,
)

__all__ = [
    "IDefinitionSchemaValidator",
    "IDefinitionAnalyzer",
    "IDefinitionSerializer",
    "IDefinitionWriter",
]
