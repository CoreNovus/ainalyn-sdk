"""
Inbound ports for Ainalyn SDK.

Inbound ports define the use cases that the application provides.
They represent "what the application can do" from the perspective
of external actors (users, CLI, API).

Examples of inbound ports (use cases):
- Validate Agent Definition
- Compile Agent Definition
- Export Agent Definition

These ports are typically implemented by use case classes in the
application layer.
"""

from __future__ import annotations

from ainalyn.application.ports.inbound.validate_agent_definition import (
    IValidateAgentDefinition,
    Severity,
    ValidationError,
    ValidationResult,
)

__all__ = [
    "IValidateAgentDefinition",
    "ValidationError",
    "ValidationResult",
    "Severity",
]
