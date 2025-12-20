"""
Ports for Ainalyn SDK (Hexagonal Architecture).

Ports define the boundaries of the application core. They are
abstract interfaces that decouple the domain from external concerns.

This module exports all port interfaces:

Inbound Ports (Primary/Driving):
- IDefinitionBuilder: Build AgentDefinitions
- IDefinitionValidator: Validate AgentDefinitions
- IDefinitionExporter: Export AgentDefinitions

Outbound Ports (Secondary/Driven):
- IDefinitionWriter: Write to external storage
- ISchemaValidator: Validate against schema

Also exports validation-related types:
- Severity: Error severity level
- ValidationError: Single validation issue
- ValidationResult: Complete validation result
"""

from __future__ import annotations

from ainalyn.ports.inbound import (
    IDefinitionBuilder,
    IDefinitionExporter,
    IDefinitionValidator,
    Severity,
    ValidationError,
    ValidationResult,
)
from ainalyn.ports.outbound import IDefinitionWriter, ISchemaValidator

__all__ = [
    # Inbound Ports
    "IDefinitionBuilder",
    "IDefinitionExporter",
    "IDefinitionValidator",
    # Outbound Ports
    "IDefinitionWriter",
    "ISchemaValidator",
    # Validation Types
    "Severity",
    "ValidationError",
    "ValidationResult",
]
