"""
Fluent Builder API for constructing Agent Definitions.

This module provides a developer-friendly fluent API for building
AgentDefinition entities. The builders use internal mutable state
but produce immutable domain entities.
"""

from __future__ import annotations

from typing import Any, Self

from ainalyn.adapters.primary.errors import (
    InvalidReferenceError,
    InvalidValueError,
    MissingRequiredFieldError,
)
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


class ModuleBuilder:
    """
    Fluent builder for Module entities.

    This builder provides a convenient API for constructing Module
    instances with validation and clear error messages.

    Example:
        >>> module = (
        ...     ModuleBuilder("http-fetcher")
        ...     .description("Fetches data from HTTP endpoints")
        ...     .input_schema({
        ...         "type": "object",
        ...         "properties": {"url": {"type": "string"}},
        ...     })
        ...     .output_schema({
        ...         "type": "object",
        ...         "properties": {"body": {"type": "string"}},
        ...     })
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a ModuleBuilder with a name.

        Args:
            name: The unique identifier for this Module. Must match [a-z0-9-]+.

        Raises:
            InvalidValueError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidValueError(
                "name",
                name,
                "Module name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._input_schema: dict[str, Any] = {}
        self._output_schema: dict[str, Any] = {}

    def description(self, desc: str) -> Self:
        """
        Set the description for this Module.

        Args:
            desc: Human-readable description of this Module's capability.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def input_schema(self, schema: dict[str, Any]) -> Self:
        """
        Set the input JSON Schema for this Module.

        Args:
            schema: JSON Schema defining the expected input structure.

        Returns:
            Self: This builder for method chaining.
        """
        self._input_schema = schema
        return self

    def output_schema(self, schema: dict[str, Any]) -> Self:
        """
        Set the output JSON Schema for this Module.

        Args:
            schema: JSON Schema defining the output structure.

        Returns:
            Self: This builder for method chaining.
        """
        self._output_schema = schema
        return self

    def build(self) -> Module:
        """
        Build and return an immutable Module entity.

        Returns:
            Module: A complete, immutable Module instance.

        Raises:
            MissingRequiredFieldError: If description is not set.
        """
        if self._description is None:
            raise MissingRequiredFieldError("description", "ModuleBuilder")

        return Module(
            name=self._name,
            description=self._description,
            input_schema=self._input_schema,
            output_schema=self._output_schema,
        )


class PromptBuilder:
    """
    Fluent builder for Prompt entities.

    This builder provides a convenient API for constructing Prompt
    instances with validation and clear error messages.

    Example:
        >>> prompt = (
        ...     PromptBuilder("data-analyzer")
        ...     .description("Analyzes structured data")
        ...     .template("Analyze this data: {{data}}")
        ...     .variables("data")
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a PromptBuilder with a name.

        Args:
            name: The unique identifier for this Prompt. Must match [a-z0-9-]+.

        Raises:
            InvalidValueError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidValueError(
                "name",
                name,
                "Prompt name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._template: str | None = None
        self._variables: list[str] = []

    def description(self, desc: str) -> Self:
        """
        Set the description for this Prompt.

        Args:
            desc: Human-readable description of this Prompt's purpose.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def template(self, tmpl: str) -> Self:
        """
        Set the prompt template content.

        Args:
            tmpl: The prompt template with {{variable}} placeholders.

        Returns:
            Self: This builder for method chaining.
        """
        self._template = tmpl
        return self

    def variables(self, *variables: str) -> Self:
        """
        Set the variables used in this template.

        Args:
            *variables: Variable names used in the template.

        Returns:
            Self: This builder for method chaining.
        """
        self._variables = list(variables)
        return self

    def build(self) -> Prompt:
        """
        Build and return an immutable Prompt entity.

        Returns:
            Prompt: A complete, immutable Prompt instance.

        Raises:
            MissingRequiredFieldError: If description or template is not set.
        """
        if self._description is None:
            raise MissingRequiredFieldError("description", "PromptBuilder")
        if self._template is None:
            raise MissingRequiredFieldError("template", "PromptBuilder")

        return Prompt(
            name=self._name,
            description=self._description,
            template=self._template,
            variables=tuple(self._variables),
        )


class ToolBuilder:
    """
    Fluent builder for Tool entities.

    This builder provides a convenient API for constructing Tool
    instances with validation and clear error messages.

    Example:
        >>> tool = (
        ...     ToolBuilder("file-writer")
        ...     .description("Writes content to a file")
        ...     .input_schema({
        ...         "type": "object",
        ...         "properties": {"path": {"type": "string"}},
        ...     })
        ...     .output_schema({
        ...         "type": "object",
        ...         "properties": {"success": {"type": "boolean"}},
        ...     })
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a ToolBuilder with a name.

        Args:
            name: The unique identifier for this Tool. Must match [a-z0-9-]+.

        Raises:
            InvalidValueError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidValueError(
                "name",
                name,
                "Tool name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._input_schema: dict[str, Any] = {}
        self._output_schema: dict[str, Any] = {}

    def description(self, desc: str) -> Self:
        """
        Set the description for this Tool.

        Args:
            desc: Human-readable description of this Tool's capability.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def input_schema(self, schema: dict[str, Any]) -> Self:
        """
        Set the input JSON Schema for this Tool.

        Args:
            schema: JSON Schema defining the expected input structure.

        Returns:
            Self: This builder for method chaining.
        """
        self._input_schema = schema
        return self

    def output_schema(self, schema: dict[str, Any]) -> Self:
        """
        Set the output JSON Schema for this Tool.

        Args:
            schema: JSON Schema defining the output structure.

        Returns:
            Self: This builder for method chaining.
        """
        self._output_schema = schema
        return self

    def build(self) -> Tool:
        """
        Build and return an immutable Tool entity.

        Returns:
            Tool: A complete, immutable Tool instance.

        Raises:
            MissingRequiredFieldError: If description is not set.
        """
        if self._description is None:
            raise MissingRequiredFieldError("description", "ToolBuilder")

        return Tool(
            name=self._name,
            description=self._description,
            input_schema=self._input_schema,
            output_schema=self._output_schema,
        )


class NodeBuilder:
    """
    Fluent builder for Node entities.

    This builder provides a convenient API for constructing Node
    instances with validation and clear error messages.

    Example:
        >>> node = (
        ...     NodeBuilder("fetch")
        ...     .description("Fetch data from API")
        ...     .uses_module("http-fetcher")
        ...     .outputs("raw_data")
        ...     .next_nodes("process")
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a NodeBuilder with a name.

        Args:
            name: The unique identifier for this Node. Must match [a-z0-9-]+.

        Raises:
            InvalidValueError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidValueError(
                "name",
                name,
                "Node name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._node_type: NodeType | None = None
        self._reference: str | None = None
        self._inputs: list[str] = []
        self._outputs: list[str] = []
        self._next_nodes: list[str] = []

    def description(self, desc: str) -> Self:
        """
        Set the description for this Node.

        Args:
            desc: Human-readable description of what this Node does.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def uses_module(self, module_name: str) -> Self:
        """
        Set this Node to reference a Module.

        Args:
            module_name: The name of the Module to reference.

        Returns:
            Self: This builder for method chaining.
        """
        self._node_type = NodeType.MODULE
        self._reference = module_name
        return self

    def uses_prompt(self, prompt_name: str) -> Self:
        """
        Set this Node to reference a Prompt.

        Args:
            prompt_name: The name of the Prompt to reference.

        Returns:
            Self: This builder for method chaining.
        """
        self._node_type = NodeType.PROMPT
        self._reference = prompt_name
        return self

    def uses_tool(self, tool_name: str) -> Self:
        """
        Set this Node to reference a Tool.

        Args:
            tool_name: The name of the Tool to reference.

        Returns:
            Self: This builder for method chaining.
        """
        self._node_type = NodeType.TOOL
        self._reference = tool_name
        return self

    def inputs(self, *input_names: str) -> Self:
        """
        Set the input parameters for this Node.

        Args:
            *input_names: Names of input parameters this Node expects.

        Returns:
            Self: This builder for method chaining.
        """
        self._inputs = list(input_names)
        return self

    def outputs(self, *output_names: str) -> Self:
        """
        Set the output parameters for this Node.

        Args:
            *output_names: Names of output parameters this Node produces.

        Returns:
            Self: This builder for method chaining.
        """
        self._outputs = list(output_names)
        return self

    def next_nodes(self, *node_names: str) -> Self:
        """
        Set the next nodes in the workflow.

        Args:
            *node_names: Names of Nodes that follow this one in the flow.

        Returns:
            Self: This builder for method chaining.
        """
        self._next_nodes = list(node_names)
        return self

    def build(self) -> Node:
        """
        Build and return an immutable Node entity.

        Returns:
            Node: A complete, immutable Node instance.

        Raises:
            MissingRequiredFieldError: If required fields are not set.
        """
        if self._description is None:
            raise MissingRequiredFieldError("description", "NodeBuilder")
        if self._node_type is None:
            raise MissingRequiredFieldError(
                "node_type",
                "NodeBuilder (call uses_module, uses_prompt, or uses_tool)",
            )
        if self._reference is None:
            raise MissingRequiredFieldError(
                "reference",
                "NodeBuilder (call uses_module, uses_prompt, or uses_tool)",
            )

        return Node(
            name=self._name,
            description=self._description,
            node_type=self._node_type,
            reference=self._reference,
            inputs=tuple(self._inputs),
            outputs=tuple(self._outputs),
            next_nodes=tuple(self._next_nodes),
        )


class WorkflowBuilder:
    """
    Fluent builder for Workflow entities.

    This builder provides a convenient API for constructing Workflow
    instances with validation and clear error messages.

    Example:
        >>> workflow = (
        ...     WorkflowBuilder("main")
        ...     .description("Main processing workflow")
        ...     .add_node(
        ...         NodeBuilder("fetch")
        ...         .description("Fetch data")
        ...         .uses_module("http-fetcher")
        ...         .build()
        ...     )
        ...     .entry_node("fetch")
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a WorkflowBuilder with a name.

        Args:
            name: The unique identifier for this Workflow. Must match [a-z0-9-]+.

        Raises:
            InvalidValueError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidValueError(
                "name",
                name,
                "Workflow name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._nodes: list[Node] = []
        self._entry_node: str | None = None

    def description(self, desc: str) -> Self:
        """
        Set the description for this Workflow.

        Args:
            desc: Human-readable description of what this Workflow accomplishes.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def add_node(self, node: Node) -> Self:
        """
        Add a Node to this Workflow.

        Args:
            node: The Node to add. Can be created using NodeBuilder.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateNameError: If a node with this name already exists.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        # Check for duplicate names
        if any(n.name == node.name for n in self._nodes):
            raise DuplicateNameError("node", node.name, f"workflow '{self._name}'")

        self._nodes.append(node)
        return self

    def nodes(self, *nodes: Node) -> Self:
        """
        Set all nodes for this Workflow at once.

        This is an alternative to calling add_node multiple times.

        Args:
            *nodes: The Nodes to add to this Workflow.

        Returns:
            Self: This builder for method chaining.

        Raises:
            DuplicateNameError: If any nodes have duplicate names.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        # Check for duplicate names
        node_names = [n.name for n in nodes]
        seen = set()
        for name in node_names:
            if name in seen:
                raise DuplicateNameError("node", name, f"workflow '{self._name}'")
            seen.add(name)

        self._nodes = list(nodes)
        return self

    def entry_node(self, node_name: str) -> Self:
        """
        Set the entry node for this Workflow.

        Args:
            node_name: The name of the starting Node in this Workflow.

        Returns:
            Self: This builder for method chaining.
        """
        self._entry_node = node_name
        return self

    def build(self) -> Workflow:
        """
        Build and return an immutable Workflow entity.

        Returns:
            Workflow: A complete, immutable Workflow instance.

        Raises:
            MissingRequiredFieldError: If required fields are not set.
            EmptyCollectionError: If no nodes have been added.
            InvalidValueError: If entry_node doesn't exist in nodes.
        """
        from ainalyn.adapters.primary.errors import EmptyCollectionError

        if self._description is None:
            raise MissingRequiredFieldError("description", "WorkflowBuilder")
        if not self._nodes:
            raise EmptyCollectionError("nodes", f"Workflow '{self._name}'")
        if self._entry_node is None:
            raise MissingRequiredFieldError("entry_node", "WorkflowBuilder")

        # Validate entry_node exists
        node_names = {n.name for n in self._nodes}
        if self._entry_node not in node_names:
            raise InvalidValueError(
                "entry_node",
                self._entry_node,
                f"Entry node '{self._entry_node}' does not exist in workflow. "
                f"Available nodes: {', '.join(sorted(node_names))}",
            )

        return Workflow(
            name=self._name,
            description=self._description,
            nodes=tuple(self._nodes),
            entry_node=self._entry_node,
        )


class AgentBuilder:
    """
    Fluent builder for AgentDefinition entities (Aggregate Root).

    This builder provides a convenient API for constructing complete
    AgentDefinition instances with validation and clear error messages.

    This is the primary entry point for creating Agent Definitions using
    the builder API.

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
            InvalidValueError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidValueError(
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
            InvalidValueError: If the version doesn't match semantic versioning.
        """
        if not DefinitionRules.is_valid_version(ver):
            raise InvalidValueError(
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
            DuplicateNameError: If a workflow with this name already exists.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        if any(w.name == workflow.name for w in self._workflows):
            raise DuplicateNameError(
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
            DuplicateNameError: If any workflows have duplicate names.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        workflow_names = [w.name for w in workflows]
        seen = set()
        for name in workflow_names:
            if name in seen:
                raise DuplicateNameError("workflow", name, f"agent '{self._name}'")
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
            DuplicateNameError: If a module with this name already exists.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        if any(m.name == module.name for m in self._modules):
            raise DuplicateNameError("module", module.name, f"agent '{self._name}'")

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
            DuplicateNameError: If any modules have duplicate names.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        module_names = [m.name for m in modules]
        seen = set()
        for name in module_names:
            if name in seen:
                raise DuplicateNameError("module", name, f"agent '{self._name}'")
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
            DuplicateNameError: If a prompt with this name already exists.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        if any(p.name == prompt.name for p in self._prompts):
            raise DuplicateNameError("prompt", prompt.name, f"agent '{self._name}'")

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
            DuplicateNameError: If any prompts have duplicate names.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        prompt_names = [p.name for p in prompts]
        seen = set()
        for name in prompt_names:
            if name in seen:
                raise DuplicateNameError("prompt", name, f"agent '{self._name}'")
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
            DuplicateNameError: If a tool with this name already exists.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        if any(t.name == tool.name for t in self._tools):
            raise DuplicateNameError("tool", tool.name, f"agent '{self._name}'")

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
            DuplicateNameError: If any tools have duplicate names.
        """
        from ainalyn.adapters.primary.errors import DuplicateNameError

        tool_names = [t.name for t in tools]
        seen = set()
        for name in tool_names:
            if name in seen:
                raise DuplicateNameError("tool", name, f"agent '{self._name}'")
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
            MissingRequiredFieldError: If required fields are not set.
            EmptyCollectionError: If no workflows have been added.
            InvalidReferenceError: If nodes reference undefined resources.
        """
        from ainalyn.adapters.primary.errors import EmptyCollectionError

        if self._version is None:
            raise MissingRequiredFieldError("version", "AgentBuilder")
        if self._description is None:
            raise MissingRequiredFieldError("description", "AgentBuilder")
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
                    raise InvalidReferenceError(node.name, "module", reference)
                if resource_type == "prompt" and reference not in prompt_names:
                    raise InvalidReferenceError(node.name, "prompt", reference)
                if resource_type == "tool" and reference not in tool_names:
                    raise InvalidReferenceError(node.name, "tool", reference)

        return AgentDefinition(
            name=self._name,
            version=self._version,
            description=self._description,
            workflows=tuple(self._workflows),
            modules=tuple(self._modules),
            prompts=tuple(self._prompts),
            tools=tuple(self._tools),
        )
