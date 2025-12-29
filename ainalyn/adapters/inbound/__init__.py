"""
Primary adapters for Ainalyn SDK.

Primary adapters (also known as driving adapters) are the entry
points through which external actors interact with the application.
They implement the inbound ports.

Examples of primary adapters:
- Fluent Builder API for constructing AgentDefinitions
- Decorator-based API for defining Agents
- CLI commands

This module exports the Fluent Builder API and error types.
"""

from __future__ import annotations

from ainalyn.adapters.inbound.builders import (
    AgentBuilder,
    ModuleBuilder,
    NodeBuilder,
    PromptBuilder,
    ToolBuilder,
    WorkflowBuilder,
)
from ainalyn.adapters.inbound.errors import (
    BuilderError,
    DuplicateNameError,
    EmptyCollectionError,
    InvalidReferenceError,
    InvalidValueError,
    MissingRequiredFieldError,
)

__all__ = [
    # Builders
    "AgentBuilder",
    "ModuleBuilder",
    "NodeBuilder",
    "PromptBuilder",
    "ToolBuilder",
    "WorkflowBuilder",
    # Errors
    "BuilderError",
    "DuplicateNameError",
    "EmptyCollectionError",
    "InvalidReferenceError",
    "InvalidValueError",
    "MissingRequiredFieldError",
]
