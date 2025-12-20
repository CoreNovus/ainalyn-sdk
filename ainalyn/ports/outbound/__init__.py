"""
Outbound ports for Ainalyn SDK.

Outbound ports (also known as driven ports or secondary ports) define
the interfaces that the application uses to interact with external
systems. These are implemented by Secondary Adapters.

This module exports:
- IDefinitionWriter: Interface for writing AgentDefinitions to files
- ISchemaValidator: Interface for schema validation
"""

from __future__ import annotations

from ainalyn.ports.outbound.schema_validator import ISchemaValidator
from ainalyn.ports.outbound.writer import IDefinitionWriter

__all__ = [
    "IDefinitionWriter",
    "ISchemaValidator",
]
