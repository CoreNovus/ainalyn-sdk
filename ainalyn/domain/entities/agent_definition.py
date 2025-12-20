from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ainalyn.domain.entities.module import Module
    from ainalyn.domain.entities.prompt import Prompt
    from ainalyn.domain.entities.tool import Tool
    from ainalyn.domain.entities.workflow import Workflow


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    """
    The complete definition of an Agent (Aggregate Root).

    AgentDefinition is the core output entity of the SDK, representing
    a complete Agent that can be submitted to the platform for review
    and governance.

    According to the Platform Constitution:
    - Agent is a Marketplace Contract Entity (task product entity)
    - AgentDefinition has description semantics only, no execution authority
    - AgentDefinition may contain workflow/node/module/prompt/tool

    The SDK's role is to compile AgentDefinitions, not to execute them.
    All execution is handled exclusively by Platform Core.

    Attributes:
        name: Unique identifier for this Agent. Must match pattern [a-z0-9-]+.
            This becomes the Agent's identity in the Marketplace.
        version: Version string for this Agent definition. Semver format
            (e.g., "1.0.0") is recommended for compatibility tracking.
        description: Human-readable description of what this Agent does.
            This is displayed to users in the Marketplace.
        workflows: Tuple of Workflows that define this Agent's task flows.
            At least one Workflow is required.
        modules: Tuple of Modules defined by this Agent. These are
            reusable capability units referenced by Nodes.
        prompts: Tuple of Prompts defined by this Agent. These are
            LLM prompt templates referenced by Nodes.
        tools: Tuple of Tools declared by this Agent. These are
            external tool interfaces referenced by Nodes.

    Example:
        >>> from ainalyn.domain.entities import (
        ...     AgentDefinition, Workflow, Node, NodeType, Module, Prompt, Tool
        ... )
        >>> agent = AgentDefinition(
        ...     name="data-pipeline-agent",
        ...     version="1.0.0",
        ...     description="An agent that fetches, processes, and stores data",
        ...     workflows=(
        ...         Workflow(
        ...             name="main",
        ...             description="Main processing workflow",
        ...             entry_node="fetch",
        ...             nodes=(...),  # Node definitions
        ...         ),
        ...     ),
        ...     modules=(
        ...         Module(name="http-fetcher", description="...", ...),
        ...     ),
        ...     prompts=(
        ...         Prompt(name="data-processor", description="...", ...),
        ...     ),
        ...     tools=(
        ...         Tool(name="file-writer", description="...", ...),
        ...     ),
        ... )
    """

    name: str
    version: str
    description: str
    workflows: tuple[Workflow, ...]
    modules: tuple[Module, ...] = ()
    prompts: tuple[Prompt, ...] = ()
    tools: tuple[Tool, ...] = ()
