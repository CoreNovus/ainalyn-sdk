from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ainalyn.domain.entities.eip_dependency import (
        CompletionCriteria,
        EIPDependency,
    )
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
    - Agent must have explicit task goal and completion criteria

    The SDK's role is to compile AgentDefinitions, not to execute them.
    All execution is handled exclusively by Platform Core.

    Attributes:
        name: Unique identifier for this Agent. Must match pattern [a-z0-9-]+.
            This becomes the Agent's identity in the Marketplace.
        version: Version string for this Agent definition. Semver format
            (e.g., "1.0.0") is recommended for compatibility tracking.
        description: Human-readable description of what this Agent does.
            This is displayed to users in the Marketplace.
        task_goal: Explicit description of the task this Agent accomplishes.
            Required for Review Gate 1 validation.
        completion_criteria: Defines success and failure conditions.
            Required for Review Gate 1 validation.
        eip_dependencies: Tuple of EIP dependencies this Agent requires.
            Used for Review Gate 5 (EIP dependency validation).
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
        ...     AgentDefinition,
        ...     Workflow,
        ...     Node,
        ...     NodeType,
        ...     Module,
        ...     Prompt,
        ...     Tool,
        ... )
        >>> from ainalyn.domain.entities.eip_dependency import (
        ...     EIPDependency,
        ...     CompletionCriteria,
        ... )
        >>> agent = AgentDefinition(
        ...     name="meeting-transcriber",
        ...     version="1.0.0",
        ...     description="Transcribes meeting recordings to text",
        ...     task_goal="Convert audio recording to structured transcript",
        ...     completion_criteria=CompletionCriteria(
        ...         success="Complete transcript with timestamps generated",
        ...         failure="Audio unrecognizable or format unsupported",
        ...     ),
        ...     eip_dependencies=(
        ...         EIPDependency(
        ...             provider="openai",
        ...             service="whisper",
        ...             config_hints={"streaming": True},
        ...         ),
        ...     ),
        ...     workflows=(...),
        ...     modules=(...),
        ... )
    """

    name: str
    version: str
    description: str
    workflows: tuple[Workflow, ...]
    task_goal: str | None = None
    completion_criteria: CompletionCriteria | None = None
    eip_dependencies: tuple[EIPDependency, ...] = ()
    modules: tuple[Module, ...] = ()
    prompts: tuple[Prompt, ...] = ()
    tools: tuple[Tool, ...] = ()
