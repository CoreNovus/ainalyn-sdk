"""
AgentBuilder - Fluent builder for AgentDefinition entities (Aggregate Root).

v0.2 AWS MVP Edition: Enhanced with AgentType, DisplayInfo, PricingStrategy,
BehaviorConfig, and JSON Schema support.

⚠️ SDK BOUNDARY WARNING ⚠️
This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
Building locally does NOT mean the platform will execute it.
All execution authority belongs to Platform Core.
"""

from __future__ import annotations

from typing import Any, Self

from ainalyn.domain.entities import (
    AgentDefinition,
    AgentType,
    BehaviorConfig,
    CompletionCriteria,
    DisplayInfo,
    EIPDependency,
    Module,
    PricingComponent,
    PricingStrategy,
    PricingType,
    Prompt,
    Tool,
    Workflow,
)
from ainalyn.domain.errors import (
    DuplicateError,
    EmptyCollectionError,
    InvalidFormatError,
    MissingFieldError,
    ReferenceError,
)
from ainalyn.domain.rules import DefinitionRules


class AgentBuilder:
    """
    Fluent builder for AgentDefinition entities (Aggregate Root).

    This builder provides a convenient API for constructing complete
    AgentDefinition instances with validation and clear error messages.

    This is the primary entry point for creating Agent Definitions using
    the builder API.

    v0.2 AWS MVP Edition adds:
    - agent_type(): Set ATOMIC or COMPOSITE type
    - display(): Set marketplace display metadata
    - pricing_fixed/pricing_usage_based(): Set pricing strategy
    - behavior(): Set execution behavior configuration
    - input_schema/output_schema(): Set JSON schemas
    - add_permission(): Add required permissions

    ⚠️ SDK BOUNDARY WARNING ⚠️
    This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
    Building locally does NOT mean the platform will execute it.
    All execution authority belongs to Platform Core.

    Example - v0.2 ATOMIC Agent:
        >>> agent = (
        ...     AgentBuilder("pdf-parser")
        ...     .version("1.0.0")
        ...     .description("Extracts text from PDF documents")
        ...     .agent_type(AgentType.ATOMIC)
        ...     .display(
        ...         name="PDF Parser",
        ...         description="Extract text from PDF documents",
        ...         category="document",
        ...     )
        ...     .task_goal("Extract all text content from a PDF file")
        ...     .completion_criteria(
        ...         CompletionCriteria(
        ...             success="Text extracted with page numbers",
        ...             failure="PDF corrupted or password protected",
        ...         )
        ...     )
        ...     .input_schema(
        ...         {"type": "object", "properties": {"file_url": {"type": "string"}}}
        ...     )
        ...     .output_schema(
        ...         {"type": "object", "properties": {"text": {"type": "string"}}}
        ...     )
        ...     .behavior(is_long_running=False, timeout_seconds=60)
        ...     .pricing_fixed(price_cents=5)
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize an AgentBuilder with a name.

        Args:
            name: The unique identifier for this Agent (agentId). Must match [a-z0-9-]+.

        Raises:
            InvalidFormatError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidFormatError(
                "name",
                name,
                "Agent name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._version: str | None = None
        self._description: str | None = None
        # v0.2 fields
        self._agent_type: AgentType | None = None
        self._display: DisplayInfo | None = None
        self._task_goal: str | None = None
        self._completion_criteria: CompletionCriteria | None = None
        self._input_schema: dict[str, Any] = {}
        self._output_schema: dict[str, Any] = {}
        self._behavior: BehaviorConfig | None = None
        self._pricing_strategy: PricingStrategy | None = None
        self._required_permissions: list[str] = []
        # Existing fields
        self._eip_dependencies: list[EIPDependency] = []
        self._workflows: list[Workflow] = []
        self._modules: list[Module] = []
        self._prompts: list[Prompt] = []
        self._tools: list[Tool] = []

    def version(self, ver: str) -> Self:
        """
        Set the version for this Agent.

        Args:
            ver: Version string. Semantic versioning (e.g., "1.0.0") is recommended.

        Returns:
            Self: This builder for method chaining.

        Raises:
            InvalidFormatError: If the version doesn't match semantic versioning.
        """
        if not DefinitionRules.is_valid_version(ver):
            raise InvalidFormatError(
                "version",
                ver,
                "Version must follow semantic versioning format (e.g., '1.0.0')",
            )
        self._version = ver
        return self

    def description(self, desc: str) -> Self:
        """
        Set the description for this Agent.

        Args:
            desc: Human-readable description of what this Agent does.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    # ========== v0.2 Methods ==========

    def agent_type(self, type_: AgentType) -> Self:
        """
        Set the Agent type (v0.2).

        Args:
            type_: AgentType.ATOMIC or AgentType.COMPOSITE.
                - ATOMIC: Code-first, executed by SDK Runtime
                - COMPOSITE: Graph-first, executed by Platform Core Graph Executor

        Returns:
            Self: This builder for method chaining.
        """
        self._agent_type = type_
        return self

    def display(
        self,
        name: str,
        description: str,
        category: str,
        icon: str | None = None,
    ) -> Self:
        """
        Set marketplace display metadata (v0.2).

        Args:
            name: Human-readable display name for marketplace.
            description: Full description for marketplace detail view.
            category: Marketplace category for discovery.
                Examples: "productivity", "finance", "developer-tools", "ai-ml".
            icon: Optional icon identifier.

        Returns:
            Self: This builder for method chaining.
        """
        self._display = DisplayInfo(
            name=name,
            description=description,
            category=category,
            icon=icon,
        )
        return self

    def input_schema(self, schema: dict[str, Any]) -> Self:
        """
        Set the input JSON Schema (v0.2).

        The input schema defines the expected structure of input data.
        Used for client-side validation and UI generation.

        Args:
            schema: JSON Schema object defining input structure.

        Returns:
            Self: This builder for method chaining.
        """
        self._input_schema = schema
        return self

    def output_schema(self, schema: dict[str, Any]) -> Self:
        """
        Set the output JSON Schema (v0.2).

        The output schema defines the structure of execution results.
        Used for result validation.

        Args:
            schema: JSON Schema object defining output structure.

        Returns:
            Self: This builder for method chaining.
        """
        self._output_schema = schema
        return self

    def behavior(
        self,
        is_long_running: bool = False,
        timeout_seconds: int = 300,
        idempotent: bool = True,
        stateless: bool = True,
    ) -> Self:
        """
        Set execution behavior configuration (v0.2).

        Args:
            is_long_running: If True, uses Heavy Route (Step Functions + SQS).
                If False (default), uses Lite Route (direct Lambda invoke).
            timeout_seconds: Maximum execution time in seconds (default: 300).
            idempotent: If True (default), safe to retry on transient failures.
            stateless: If True (default), no persistent state between invocations.

        Returns:
            Self: This builder for method chaining.
        """
        self._behavior = BehaviorConfig(
            is_long_running=is_long_running,
            timeout_seconds=timeout_seconds,
            idempotent=idempotent,
            stateless=stateless,
        )
        return self

    def pricing_fixed(self, price_cents: int, currency: str = "USD") -> Self:
        """
        Set fixed pricing strategy (v0.2).

        IMPORTANT: This is a HINT only. Actual billing is handled by Platform Core.
        SDK does NOT calculate or return fees (Gate 4 compliance).

        Args:
            price_cents: Price in cents per successful execution.
                Example: 10 = $0.10 per execution.
            currency: Currency code (default: "USD").

        Returns:
            Self: This builder for method chaining.
        """
        self._pricing_strategy = PricingStrategy(
            type=PricingType.FIXED,
            fixed_price_cents=price_cents,
            currency=currency,
        )
        return self

    def pricing_usage_based(
        self,
        rate_per_unit: float,
        unit: str,
        currency: str = "USD",
    ) -> Self:
        """
        Set usage-based pricing strategy (v0.2).

        IMPORTANT: This is a HINT only. Actual billing is handled by Platform Core.
        SDK does NOT calculate or return fees (Gate 4 compliance).

        Args:
            rate_per_unit: Rate per usage unit.
                Example: 0.001 = $0.001 per unit.
            unit: Name of usage unit.
                Examples: "token", "minute", "page", "request".
            currency: Currency code (default: "USD").

        Returns:
            Self: This builder for method chaining.
        """
        self._pricing_strategy = PricingStrategy(
            type=PricingType.USAGE_BASED,
            usage_rate_per_unit=rate_per_unit,
            usage_unit=unit,
            currency=currency,
        )
        return self

    def pricing_composite(
        self,
        components: list[PricingComponent],
        currency: str = "USD",
    ) -> Self:
        """
        Set composite pricing strategy (v0.2).

        Composite pricing combines fixed base fee with usage-based overage.

        IMPORTANT: This is a HINT only. Actual billing is handled by Platform Core.
        SDK does NOT calculate or return fees (Gate 4 compliance).

        Args:
            components: List of pricing components.
            currency: Currency code (default: "USD").

        Returns:
            Self: This builder for method chaining.
        """
        self._pricing_strategy = PricingStrategy(
            type=PricingType.COMPOSITE,
            components=tuple(components),
            currency=currency,
        )
        return self

    def add_permission(self, permission: str) -> Self:
        """
        Add a required permission (v0.2).

        Args:
            permission: Permission string this Agent requires.

        Returns:
            Self: This builder for method chaining.
        """
        if permission not in self._required_permissions:
            self._required_permissions.append(permission)
        return self

    def permissions(self, *permissions: str) -> Self:
        """
        Set all required permissions at once (v0.2).

        Args:
            *permissions: Permission strings this Agent requires.

        Returns:
            Self: This builder for method chaining.
        """
        self._required_permissions = list(dict.fromkeys(permissions))
        return self

    # ========== Existing Methods ==========

    def task_goal(self, goal: str) -> Self:
        """
        Set the task goal for this Agent.

        The task goal is a clear description of what this Agent accomplishes.
        This is required for Platform Core Review Gate 1 validation.

        Args:
            goal: Description of the task this Agent completes.

        Returns:
            Self: This builder for method chaining.
        """
        self._task_goal = goal
        return self

    def completion_criteria(self, criteria: CompletionCriteria) -> Self:
        """
        Set the completion criteria for this Agent.

        Completion criteria define what constitutes success or failure.
        This is required for Platform Core Review Gate 1 validation.

        Args:
            criteria: CompletionCriteria instance defining success/failure conditions.

        Returns:
            Self: This builder for method chaining.
        """
        self._completion_criteria = criteria
        return self

    def add_eip_dependency(self, dependency: EIPDependency) -> Self:
        """
        Add an EIP dependency to this Agent.

        EIP dependencies declare which Execution Implementation Providers
        this Agent requires. This is used for Platform Core Review Gate 5.

        Args:
            dependency: EIPDependency instance declaring the required EIP.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If an EIP with this provider/service already exists.
        """
        key = (dependency.provider, dependency.service)
        for existing in self._eip_dependencies:
            if (existing.provider, existing.service) == key:
                raise DuplicateError(
                    "eip_dependency",
                    f"{dependency.provider}/{dependency.service}",
                    f"agent '{self._name}'",
                )

        self._eip_dependencies.append(dependency)
        return self

    def add_workflow(self, workflow: Workflow) -> Self:
        """
        Add a Workflow to this Agent.

        Args:
            workflow: The Workflow to add. Can be created using WorkflowBuilder.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If a workflow with this name already exists.
        """
        if any(w.name == workflow.name for w in self._workflows):
            raise DuplicateError(
                "workflow",
                workflow.name,
                f"agent '{self._name}'",
            )

        self._workflows.append(workflow)
        return self

    def workflows(self, *workflows: Workflow) -> Self:
        """
        Set all workflows for this Agent at once.

        This is an alternative to calling add_workflow multiple times.

        Args:
            *workflows: The Workflows to add to this Agent.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If any workflows have duplicate names.
        """
        workflow_names = [w.name for w in workflows]
        seen = set()
        for name in workflow_names:
            if name in seen:
                raise DuplicateError("workflow", name, f"agent '{self._name}'")
            seen.add(name)

        self._workflows = list(workflows)
        return self

    def add_module(self, module: Module) -> Self:
        """
        Add a Module to this Agent.

        Args:
            module: The Module to add. Can be created using ModuleBuilder.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If a module with this name already exists.
        """
        if any(m.name == module.name for m in self._modules):
            raise DuplicateError("module", module.name, f"agent '{self._name}'")

        self._modules.append(module)
        return self

    def modules(self, *modules: Module) -> Self:
        """
        Set all modules for this Agent at once.

        Args:
            *modules: The Modules to add to this Agent.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If any modules have duplicate names.
        """
        module_names = [m.name for m in modules]
        seen = set()
        for name in module_names:
            if name in seen:
                raise DuplicateError("module", name, f"agent '{self._name}'")
            seen.add(name)

        self._modules = list(modules)
        return self

    def add_prompt(self, prompt: Prompt) -> Self:
        """
        Add a Prompt to this Agent.

        Args:
            prompt: The Prompt to add. Can be created using PromptBuilder.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If a prompt with this name already exists.
        """
        if any(p.name == prompt.name for p in self._prompts):
            raise DuplicateError("prompt", prompt.name, f"agent '{self._name}'")

        self._prompts.append(prompt)
        return self

    def prompts(self, *prompts: Prompt) -> Self:
        """
        Set all prompts for this Agent at once.

        Args:
            *prompts: The Prompts to add to this Agent.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If any prompts have duplicate names.
        """
        prompt_names = [p.name for p in prompts]
        seen = set()
        for name in prompt_names:
            if name in seen:
                raise DuplicateError("prompt", name, f"agent '{self._name}'")
            seen.add(name)

        self._prompts = list(prompts)
        return self

    def add_tool(self, tool: Tool) -> Self:
        """
        Add a Tool to this Agent.

        Args:
            tool: The Tool to add. Can be created using ToolBuilder.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If a tool with this name already exists.
        """
        if any(t.name == tool.name for t in self._tools):
            raise DuplicateError("tool", tool.name, f"agent '{self._name}'")

        self._tools.append(tool)
        return self

    def tools(self, *tools: Tool) -> Self:
        """
        Set all tools for this Agent at once.

        Args:
            *tools: The Tools to add to this Agent.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateError: If any tools have duplicate names.
        """
        tool_names = [t.name for t in tools]
        seen = set()
        for name in tool_names:
            if name in seen:
                raise DuplicateError("tool", name, f"agent '{self._name}'")
            seen.add(name)

        self._tools = list(tools)
        return self

    def build(self) -> AgentDefinition:
        """
        Build and return an immutable AgentDefinition entity.

        This method performs validation to ensure:
        - All required fields are set (v0.2: includes agent_type)
        - For COMPOSITE agents: at least one workflow is defined
        - All node references point to existing resources

        Returns:
            AgentDefinition: A complete, immutable AgentDefinition instance.

        Raises:
            MissingFieldError: If required fields are not set.
            EmptyCollectionError: If COMPOSITE agent has no workflows.
            ReferenceError: If nodes reference undefined resources.
        """
        # v0.2: agent_type is now required
        if self._agent_type is None:
            raise MissingFieldError("agent_type", "AgentBuilder")
        if self._version is None:
            raise MissingFieldError("version", "AgentBuilder")
        if self._description is None:
            raise MissingFieldError("description", "AgentBuilder")

        # COMPOSITE agents must have at least one workflow
        if self._agent_type == AgentType.COMPOSITE and not self._workflows:
            raise EmptyCollectionError("workflows", f"COMPOSITE Agent '{self._name}'")

        # Build sets of defined resource names
        module_names = {m.name for m in self._modules}
        prompt_names = {p.name for p in self._prompts}
        tool_names = {t.name for t in self._tools}

        # Validate all node references
        for workflow in self._workflows:
            for node in workflow.nodes:
                resource_type = node.node_type.value
                reference = node.reference

                if resource_type == "module" and reference not in module_names:
                    raise ReferenceError(node.name, "module", reference)
                if resource_type == "prompt" and reference not in prompt_names:
                    raise ReferenceError(node.name, "prompt", reference)
                if resource_type == "tool" and reference not in tool_names:
                    raise ReferenceError(node.name, "tool", reference)

        return AgentDefinition(
            name=self._name,
            version=self._version,
            description=self._description,
            agent_type=self._agent_type,
            # v0.2 fields
            display=self._display,
            task_goal=self._task_goal,
            completion_criteria=self._completion_criteria,
            input_schema=self._input_schema,
            output_schema=self._output_schema,
            behavior=self._behavior,
            pricing_strategy=self._pricing_strategy,
            required_permissions=tuple(self._required_permissions),
            # Existing fields
            eip_dependencies=tuple(self._eip_dependencies),
            workflows=tuple(self._workflows),
            modules=tuple(self._modules),
            prompts=tuple(self._prompts),
            tools=tuple(self._tools),
        )
