"""
Domain layer for Ainalyn SDK.

The domain layer contains the core business logic and entities
that are independent of any external concerns. This layer:

- Defines the core entities (AgentDefinition, Workflow, Node, etc.)
- Contains business rules for validation
- Defines domain errors (compile-time errors)
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
from ainalyn.domain.errors import (
    CyclicDependencyError,
    DefinitionError,
    DomainError,
    DuplicateError,
    EmptyCollectionError,
    InvalidFormatError,
    MissingFieldError,
    ReferenceError,
    UnreachableNodeError,
)
from ainalyn.domain.rules import DefinitionRules

__all__ = [
    # Entities
    "AgentDefinition",
    "Module",
    "Node",
    "NodeType",
    "Prompt",
    "Tool",
    "Workflow",
    # Rules
    "DefinitionRules",
    # Errors
    "DomainError",
    "DefinitionError",
    "MissingFieldError",
    "InvalidFormatError",
    "ReferenceError",
    "DuplicateError",
    "EmptyCollectionError",
    "CyclicDependencyError",
    "UnreachableNodeError",
]
