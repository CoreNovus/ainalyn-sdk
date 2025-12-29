"""
AgentBuilder - Fluent builder for AgentDefinition entities (Aggregate Root).

⚠️ SDK BOUNDARY WARNING ⚠️
This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
Building locally does NOT mean the platform will execute it.
All execution authority belongs to Platform Core.
"""

from __future__ import annotations

from typing import Self

from ainalyn.domain.errors import (
    DuplicateError,
    EmptyCollectionError,
    InvalidFormatError,
    MissingFieldError,
    ReferenceError,
)
from ainalyn.domain.entities import (
    AgentDefinition,
    Module,
    Prompt,
    Tool,
    Workflow,
)
from ainalyn.domain.rules import DefinitionRules


class AgentBuilder:
    """
    Fluent builder for AgentDefinition entities (Aggregate Root).

    This builder provides a convenient API for constructing complete
    AgentDefinition instances with validation and clear error messages.

    This is the primary entry point for creating Agent Definitions using
    the builder API.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
    Building locally does NOT mean the platform will execute it.
    All execution authority belongs to Platform Core.

    Example:
        >>> agent = (
        ...     AgentBuilder("my-agent")
        ...     .version("1.0.0")
        ...     .description("My first agent")
        ...     .add_module(
        ...         ModuleBuilder("http-fetcher")
        ...         .description("Fetches HTTP data")
        ...         .build()
        ...     )
        ...     .add_workflow(
        ...         WorkflowBuilder("main")
        ...         .description("Main workflow")
        ...         .add_node(
        ...             NodeBuilder("fetch")
        ...             .description("Fetch data")
        ...             .uses_module("http-fetcher")
        ...             .build()
        ...         )
        ...         .entry_node("fetch")
        ...         .build()
        ...     )
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize an AgentBuilder with a name.

        Args:
            name: The unique identifier for this Agent. Must match [a-z0-9-]+.

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
        - All required fields are set
        - At least one workflow is defined
        - All node references point to existing resources

        Returns:
            AgentDefinition: A complete, immutable AgentDefinition instance.

        Raises:
            MissingFieldError: If required fields are not set.
            EmptyCollectionError: If no workflows have been added.
            ReferenceError: If nodes reference undefined resources.
        """
        if self._version is None:
            raise MissingFieldError("version", "AgentBuilder")
        if self._description is None:
            raise MissingFieldError("description", "AgentBuilder")
        if not self._workflows:
            raise EmptyCollectionError("workflows", f"Agent '{self._name}'")

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
            workflows=tuple(self._workflows),
            modules=tuple(self._modules),
            prompts=tuple(self._prompts),
            tools=tuple(self._tools),
        )
