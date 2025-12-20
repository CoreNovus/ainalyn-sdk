"""
Inbound ports for Ainalyn SDK.

Inbound ports (also known as driving ports or primary ports) define
the interfaces through which external actors interact with the
application. These are implemented by Primary Adapters.

This module exports:
- IDefinitionBuilder: Interface for building AgentDefinitions
- IDefinitionValidator: Interface for validating AgentDefinitions
- IDefinitionExporter: Interface for exporting AgentDefinitions
- Validation-related data classes (Severity, ValidationError, ValidationResult)
"""

from __future__ import annotations

from ainalyn.ports.inbound.builder import IDefinitionBuilder
from ainalyn.ports.inbound.exporter import IDefinitionExporter
from ainalyn.ports.inbound.validator import (
    IDefinitionValidator,
    Severity,
    ValidationError,
    ValidationResult,
)

__all__ = [
    "IDefinitionBuilder",
    "IDefinitionExporter",
    "IDefinitionValidator",
    "Severity",
    "ValidationError",
    "ValidationResult",
]
