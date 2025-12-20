"""
Domain entities for Ainalyn SDK.

This module exports all core domain entities that represent the
fundamental building blocks of an Agent Definition.

These entities are immutable (frozen dataclasses) and represent
pure description, with no execution semantics.
"""

from __future__ import annotations

from ainalyn.domain.entities.agent_definition import AgentDefinition
from ainalyn.domain.entities.module import Module
from ainalyn.domain.entities.node import Node, NodeType
from ainalyn.domain.entities.prompt import Prompt
from ainalyn.domain.entities.tool import Tool
from ainalyn.domain.entities.workflow import Workflow

__all__ = [
    "AgentDefinition",
    "Module",
    "Node",
    "NodeType",
    "Prompt",
    "Tool",
    "Workflow",
]
