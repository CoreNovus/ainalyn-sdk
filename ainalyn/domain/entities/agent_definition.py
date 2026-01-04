"""
Agent Definition - The Aggregate Root of the SDK.

v0.2 AWS MVP Edition: Enhanced with AgentType, DisplayInfo, PricingStrategy,
BehaviorConfig, and JSON Schema support for input/output validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ainalyn.domain.entities.agent_type import AgentType
    from ainalyn.domain.entities.behavior_config import BehaviorConfig
    from ainalyn.domain.entities.display_info import DisplayInfo
    from ainalyn.domain.entities.eip_dependency import (
        CompletionCriteria,
        EIPDependency,
    )
    from ainalyn.domain.entities.module import Module
    from ainalyn.domain.entities.pricing_strategy import PricingStrategy
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

    v0.2 AWS MVP Edition Additions:
    - agent_type: ATOMIC (code-first) or COMPOSITE (graph-first)
    - display: Marketplace presentation metadata
    - pricing_strategy: Monetization model description
    - behavior: Execution behavior configuration
    - input_schema/output_schema: JSON Schema for validation
    - required_permissions: Permission requirements

    Attributes:
        name: Unique identifier for this Agent (agentId). Must match pattern [a-z0-9-]+.
            This becomes the Agent's identity in the Marketplace.
        version: Version string for this Agent definition. Semver format
            (e.g., "1.0.0") is required for compatibility tracking.
        description: Human-readable description of what this Agent does.
            This is displayed to users in the Marketplace.
        agent_type: Type of Agent - ATOMIC (code-first) or COMPOSITE (graph-first).
            Determines execution path: SDK Runtime vs Platform Graph Executor.
        display: Marketplace display metadata (name, description, category, icon).
        task_goal: Explicit description of the task this Agent accomplishes.
            Required for Review Gate 1 validation.
        completion_criteria: Defines success and failure conditions.
            Required for Review Gate 1 validation.
        input_schema: JSON Schema defining the expected input structure.
            Used for client-side validation and UI generation.
        output_schema: JSON Schema defining the output structure.
            Used for result validation.
        behavior: Execution behavior configuration (timeout, routing, idempotency).
            Affects Platform Core's routing decisions (Lite vs Heavy route).
        pricing_strategy: Monetization model description.
            IMPORTANT: This is a HINT only. Actual billing is by Platform Core.
        required_permissions: Tuple of permission strings this Agent requires.
        eip_dependencies: Tuple of EIP dependencies this Agent requires.
            Used for Review Gate 5 (EIP dependency validation).
        workflows: Tuple of Workflows that define this Agent's task flows.
            At least one Workflow is required for COMPOSITE agents.
        modules: Tuple of Modules defined by this Agent. These are
            reusable capability units referenced by Nodes.
        prompts: Tuple of Prompts defined by this Agent. These are
            LLM prompt templates referenced by Nodes.
        tools: Tuple of Tools declared by this Agent. These are
            external tool interfaces referenced by Nodes.

    Example - ATOMIC Agent:
        >>> from ainalyn.domain.entities import (
        ...     AgentDefinition,
        ...     AgentType,
        ...     DisplayInfo,
        ...     BehaviorConfig,
        ...     PricingStrategy,
        ...     PricingType,
        ...     CompletionCriteria,
        ... )
        >>> agent = AgentDefinition(
        ...     name="pdf-parser",
        ...     version="1.0.0",
        ...     description="Extracts text from PDF documents",
        ...     agent_type=AgentType.ATOMIC,
        ...     display=DisplayInfo(
        ...         name="PDF Parser",
        ...         description="Extract text from PDF documents",
        ...         category="document",
        ...     ),
        ...     task_goal="Extract all text content from a PDF file",
        ...     completion_criteria=CompletionCriteria(
        ...         success="Text extracted with page numbers",
        ...         failure="PDF corrupted or password protected",
        ...     ),
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {"file_url": {"type": "string"}},
        ...     },
        ...     output_schema={
        ...         "type": "object",
        ...         "properties": {"text": {"type": "string"}},
        ...     },
        ...     behavior=BehaviorConfig(is_long_running=False, timeout_seconds=60),
        ...     pricing_strategy=PricingStrategy(
        ...         type=PricingType.FIXED, fixed_price_cents=5
        ...     ),
        ...     workflows=(),  # ATOMIC agents may have no workflow
        ... )
    """

    # Required fields
    name: str
    version: str
    description: str
    agent_type: AgentType

    # v0.2 Marketplace metadata
    display: DisplayInfo | None = None

    # v0.2 Contract completeness (Gate 1)
    task_goal: str | None = None
    completion_criteria: CompletionCriteria | None = None

    # v0.2 Schema definitions
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)

    # v0.2 Behavior configuration
    behavior: BehaviorConfig | None = None

    # v0.2 Pricing (hint only - Gate 4 compliance)
    pricing_strategy: PricingStrategy | None = None

    # v0.2 Permissions
    required_permissions: tuple[str, ...] = ()

    # EIP dependencies (Gate 5)
    eip_dependencies: tuple[EIPDependency, ...] = ()

    # Workflow components
    workflows: tuple[Workflow, ...] = ()
    modules: tuple[Module, ...] = ()
    prompts: tuple[Prompt, ...] = ()
    tools: tuple[Tool, ...] = ()
