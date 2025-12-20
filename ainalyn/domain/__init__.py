"""
Domain layer for Ainalyn SDK.

The domain layer contains the core business logic and entities
that are independent of any external concerns. This layer:

- Defines the core entities (AgentDefinition, Workflow, Node, etc.)
- Contains business rules for validation
- Has no dependencies on adapters, frameworks, or I/O

This module re-exports commonly used domain components.
"""

from __future__ import annotations

from ainalyn.domain.entities import (
    AgentDefinition,
    Module,
    Node,
    NodeType,
    Prompt,
    Tool,
    Workflow,
)
from ainalyn.domain.rules import DefinitionRules

__all__ = [
    "AgentDefinition",
    "DefinitionRules",
    "Module",
    "Node",
    "NodeType",
    "Prompt",
    "Tool",
    "Workflow",
]
