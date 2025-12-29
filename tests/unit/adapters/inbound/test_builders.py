"""Unit tests for builder classes."""

from __future__ import annotations

import pytest

from ainalyn.adapters.inbound.builders import (
    AgentBuilder,
    ModuleBuilder,
    NodeBuilder,
    PromptBuilder,
    ToolBuilder,
    WorkflowBuilder,
)
from ainalyn.adapters.inbound.errors import (
    DuplicateNameError,
    EmptyCollectionError,
    InvalidReferenceError,
    InvalidValueError,
    MissingRequiredFieldError,
)
from ainalyn.domain.entities import (
    Module,
    Node,
    NodeType,
    Prompt,
    Tool,
    Workflow,
)


class TestModuleBuilder:
    """Tests for ModuleBuilder."""

    def test_build_minimal_module(self) -> None:
        """Test building a module with minimal required fields."""
        module = (
            ModuleBuilder("http-fetcher")
            .description("Fetches data from HTTP endpoints")
            .build()
        )

        assert isinstance(module, Module)
        assert module.name == "http-fetcher"
        assert module.description == "Fetches data from HTTP endpoints"
        assert module.input_schema == {}
        assert module.output_schema == {}

    def test_build_module_with_schemas(self) -> None:
        """Test building a module with input/output schemas."""
        input_schema = {"type": "object", "properties": {"url": {"type": "string"}}}
        output_schema = {"type": "object", "properties": {"body": {"type": "string"}}}

        module = (
            ModuleBuilder("http-fetcher")
            .description("Fetches data")
            .input_schema(input_schema)
            .output_schema(output_schema)
            .build()
        )

        assert module.input_schema == input_schema
        assert module.output_schema == output_schema

    def test_module_builder_invalid_name(self) -> None:
        """Test that invalid names are rejected."""
        with pytest.raises(InvalidValueError) as exc_info:
            ModuleBuilder("Invalid Name")

        assert "name" in str(exc_info.value)
        assert "lowercase" in str(exc_info.value)

    def test_module_builder_missing_description(self) -> None:
        """Test that missing description raises error."""
        builder = ModuleBuilder("http-fetcher")

        with pytest.raises(MissingRequiredFieldError) as exc_info:
            builder.build()

        assert exc_info.value.field_name == "description"
        assert exc_info.value.entity_type == "ModuleBuilder"

    def test_module_builder_fluent_interface(self) -> None:
        """Test that methods return self for chaining."""
        builder = ModuleBuilder("test")
        assert builder.description("test") is builder
        assert builder.input_schema({}) is builder
        assert builder.output_schema({}) is builder


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    def test_build_minimal_prompt(self) -> None:
        """Test building a prompt with minimal required fields."""
        prompt = (
            PromptBuilder("analyzer")
            .description("Analyzes data")
            .template("Analyze: {{data}}")
            .build()
        )

        assert isinstance(prompt, Prompt)
        assert prompt.name == "analyzer"
        assert prompt.description == "Analyzes data"
        assert prompt.template == "Analyze: {{data}}"
        assert prompt.variables == ()

    def test_build_prompt_with_variables(self) -> None:
        """Test building a prompt with variables."""
        prompt = (
            PromptBuilder("analyzer")
            .description("Analyzes data")
            .template("Analyze {{data}} focusing on {{focus}}")
            .variables("data", "focus")
            .build()
        )

        assert prompt.variables == ("data", "focus")

    def test_prompt_builder_invalid_name(self) -> None:
        """Test that invalid names are rejected."""
        with pytest.raises(InvalidValueError):
            PromptBuilder("Invalid_Name")

    def test_prompt_builder_missing_description(self) -> None:
        """Test that missing description raises error."""
        builder = PromptBuilder("test").template("test")

        with pytest.raises(MissingRequiredFieldError) as exc_info:
            builder.build()

        assert exc_info.value.field_name == "description"

    def test_prompt_builder_missing_template(self) -> None:
        """Test that missing template raises error."""
        builder = PromptBuilder("test").description("test")

        with pytest.raises(MissingRequiredFieldError) as exc_info:
            builder.build()

        assert exc_info.value.field_name == "template"


class TestToolBuilder:
    """Tests for ToolBuilder."""

    def test_build_minimal_tool(self) -> None:
        """Test building a tool with minimal required fields."""
        tool = ToolBuilder("file-writer").description("Writes files").build()

        assert isinstance(tool, Tool)
        assert tool.name == "file-writer"
        assert tool.description == "Writes files"
        assert tool.input_schema == {}
        assert tool.output_schema == {}

    def test_build_tool_with_schemas(self) -> None:
        """Test building a tool with schemas."""
        tool = (
            ToolBuilder("file-writer")
            .description("Writes files")
            .input_schema({"type": "object"})
            .output_schema({"type": "boolean"})
            .build()
        )

        assert tool.input_schema == {"type": "object"}
        assert tool.output_schema == {"type": "boolean"}

    def test_tool_builder_invalid_name(self) -> None:
        """Test that invalid names are rejected."""
        with pytest.raises(InvalidValueError):
            ToolBuilder("Tool With Spaces")


class TestNodeBuilder:
    """Tests for NodeBuilder."""

    def test_build_node_with_module(self) -> None:
        """Test building a node that uses a module."""
        node = (
            NodeBuilder("fetch")
            .description("Fetch data")
            .uses_module("http-fetcher")
            .outputs("data")
            .next_nodes("process")
            .build()
        )

        assert isinstance(node, Node)
        assert node.name == "fetch"
        assert node.description == "Fetch data"
        assert node.node_type == NodeType.MODULE
        assert node.reference == "http-fetcher"
        assert node.outputs == ("data",)
        assert node.next_nodes == ("process",)

    def test_build_node_with_prompt(self) -> None:
        """Test building a node that uses a prompt."""
        node = (
            NodeBuilder("analyze")
            .description("Analyze data")
            .uses_prompt("analyzer")
            .inputs("data")
            .outputs("result")
            .build()
        )

        assert node.node_type == NodeType.PROMPT
        assert node.reference == "analyzer"
        assert node.inputs == ("data",)

    def test_build_node_with_tool(self) -> None:
        """Test building a node that uses a tool."""
        node = (
            NodeBuilder("write")
            .description("Write data")
            .uses_tool("file-writer")
            .inputs("result")
            .build()
        )

        assert node.node_type == NodeType.TOOL
        assert node.reference == "file-writer"
        assert node.next_nodes == ()

    def test_node_builder_missing_description(self) -> None:
        """Test that missing description raises error."""
        builder = NodeBuilder("test").uses_module("test-module")

        with pytest.raises(MissingRequiredFieldError) as exc_info:
            builder.build()

        assert exc_info.value.field_name == "description"

    def test_node_builder_missing_resource_type(self) -> None:
        """Test that missing resource type raises error."""
        builder = NodeBuilder("test").description("test")

        with pytest.raises(MissingRequiredFieldError) as exc_info:
            builder.build()

        assert "node_type" in exc_info.value.field_name


class TestWorkflowBuilder:
    """Tests for WorkflowBuilder."""

    def test_build_simple_workflow(self) -> None:
        """Test building a workflow with one node."""
        node = (
            NodeBuilder("fetch")
            .description("Fetch data")
            .uses_module("http-fetcher")
            .build()
        )

        workflow = (
            WorkflowBuilder("main")
            .description("Main workflow")
            .add_node(node)
            .entry_node("fetch")
            .build()
        )

        assert isinstance(workflow, Workflow)
        assert workflow.name == "main"
        assert workflow.description == "Main workflow"
        assert len(workflow.nodes) == 1
        assert workflow.entry_node == "fetch"

    def test_build_workflow_with_multiple_nodes(self) -> None:
        """Test building a workflow with multiple nodes."""
        node1 = (
            NodeBuilder("fetch")
            .description("Fetch")
            .uses_module("http-fetcher")
            .next_nodes("process")
            .build()
        )
        node2 = (
            NodeBuilder("process")
            .description("Process")
            .uses_prompt("analyzer")
            .build()
        )

        workflow = (
            WorkflowBuilder("main")
            .description("Main workflow")
            .add_node(node1)
            .add_node(node2)
            .entry_node("fetch")
            .build()
        )

        assert len(workflow.nodes) == 2

    def test_workflow_builder_nodes_method(self) -> None:
        """Test setting all nodes at once."""
        node1 = NodeBuilder("n1").description("N1").uses_module("m1").build()
        node2 = NodeBuilder("n2").description("N2").uses_module("m2").build()

        workflow = (
            WorkflowBuilder("main")
            .description("Main")
            .nodes(node1, node2)
            .entry_node("n1")
            .build()
        )

        assert len(workflow.nodes) == 2

    def test_workflow_builder_duplicate_node_names(self) -> None:
        """Test that duplicate node names are rejected."""
        node1 = NodeBuilder("fetch").description("Fetch 1").uses_module("m1").build()
        node2 = NodeBuilder("fetch").description("Fetch 2").uses_module("m2").build()

        builder = WorkflowBuilder("main").description("Main").add_node(node1)

        with pytest.raises(DuplicateNameError) as exc_info:
            builder.add_node(node2)

        assert exc_info.value.entity_type == "node"
        assert exc_info.value.name == "fetch"

    def test_workflow_builder_empty_nodes(self) -> None:
        """Test that empty workflow raises error."""
        builder = WorkflowBuilder("main").description("Main").entry_node("fetch")

        with pytest.raises(EmptyCollectionError) as exc_info:
            builder.build()

        assert exc_info.value.collection_name == "nodes"

    def test_workflow_builder_invalid_entry_node(self) -> None:
        """Test that invalid entry node raises error."""
        node = NodeBuilder("fetch").description("Fetch").uses_module("m").build()

        builder = (
            WorkflowBuilder("main")
            .description("Main")
            .add_node(node)
            .entry_node("nonexistent")
        )

        with pytest.raises(InvalidValueError) as exc_info:
            builder.build()

        assert "entry_node" in exc_info.value.field_name
        assert "nonexistent" in str(exc_info.value)


class TestAgentBuilder:
    """Tests for AgentBuilder."""

    def test_build_minimal_agent(self) -> None:
        """Test building an agent with minimal configuration."""
        node = NodeBuilder("n").description("N").uses_module("m").build()
        workflow = (
            WorkflowBuilder("main")
            .description("Main")
            .add_node(node)
            .entry_node("n")
            .build()
        )
        module = ModuleBuilder("m").description("Module").build()

        agent = (
            AgentBuilder("my-agent")
            .version("1.0.0")
            .description("My agent")
            .add_module(module)
            .add_workflow(workflow)
            .build()
        )

        assert agent.name == "my-agent"
        assert agent.version == "1.0.0"
        assert agent.description == "My agent"
        assert len(agent.workflows) == 1
        assert len(agent.modules) == 1

    def test_build_agent_with_all_resources(self) -> None:
        """Test building an agent with modules, prompts, and tools."""
        module = ModuleBuilder("m").description("M").build()
        prompt = PromptBuilder("p").description("P").template("T").build()
        tool = ToolBuilder("t").description("T").build()

        node1 = (
            NodeBuilder("n1").description("N1").uses_module("m").next_nodes("n2").build()
        )
        node2 = (
            NodeBuilder("n2").description("N2").uses_prompt("p").next_nodes("n3").build()
        )
        node3 = NodeBuilder("n3").description("N3").uses_tool("t").build()

        workflow = (
            WorkflowBuilder("main")
            .description("Main")
            .nodes(node1, node2, node3)
            .entry_node("n1")
            .build()
        )

        agent = (
            AgentBuilder("my-agent")
            .version("1.0.0")
            .description("My agent")
            .add_module(module)
            .add_prompt(prompt)
            .add_tool(tool)
            .add_workflow(workflow)
            .build()
        )

        assert len(agent.modules) == 1
        assert len(agent.prompts) == 1
        assert len(agent.tools) == 1
        assert len(agent.workflows) == 1

    def test_agent_builder_invalid_version(self) -> None:
        """Test that invalid version is rejected."""
        with pytest.raises(InvalidValueError) as exc_info:
            AgentBuilder("test").version("invalid")

        assert "version" in exc_info.value.field_name
        assert "semantic versioning" in str(exc_info.value)

    def test_agent_builder_missing_version(self) -> None:
        """Test that missing version raises error."""
        module = ModuleBuilder("m").description("M").build()
        node = NodeBuilder("n").description("N").uses_module("m").build()
        workflow = (
            WorkflowBuilder("w")
            .description("W")
            .add_node(node)
            .entry_node("n")
            .build()
        )

        builder = (
            AgentBuilder("test")
            .description("Test")
            .add_module(module)
            .add_workflow(workflow)
        )

        with pytest.raises(MissingRequiredFieldError) as exc_info:
            builder.build()

        assert exc_info.value.field_name == "version"

    def test_agent_builder_empty_workflows(self) -> None:
        """Test that agent with no workflows raises error."""
        builder = AgentBuilder("test").version("1.0.0").description("Test")

        with pytest.raises(EmptyCollectionError) as exc_info:
            builder.build()

        assert exc_info.value.collection_name == "workflows"

    def test_agent_builder_undefined_module_reference(self) -> None:
        """Test that undefined module reference raises error."""
        node = NodeBuilder("n").description("N").uses_module("undefined").build()
        workflow = (
            WorkflowBuilder("w")
            .description("W")
            .add_node(node)
            .entry_node("n")
            .build()
        )

        builder = (
            AgentBuilder("test")
            .version("1.0.0")
            .description("Test")
            .add_workflow(workflow)
        )

        with pytest.raises(InvalidReferenceError) as exc_info:
            builder.build()

        assert exc_info.value.resource_type == "module"
        assert exc_info.value.reference == "undefined"

    def test_agent_builder_undefined_prompt_reference(self) -> None:
        """Test that undefined prompt reference raises error."""
        node = NodeBuilder("n").description("N").uses_prompt("undefined").build()
        workflow = (
            WorkflowBuilder("w")
            .description("W")
            .add_node(node)
            .entry_node("n")
            .build()
        )

        builder = (
            AgentBuilder("test")
            .version("1.0.0")
            .description("Test")
            .add_workflow(workflow)
        )

        with pytest.raises(InvalidReferenceError) as exc_info:
            builder.build()

        assert exc_info.value.resource_type == "prompt"

    def test_agent_builder_duplicate_workflow_names(self) -> None:
        """Test that duplicate workflow names are rejected."""
        module = ModuleBuilder("m").description("M").build()
        node = NodeBuilder("n").description("N").uses_module("m").build()
        workflow1 = (
            WorkflowBuilder("w")
            .description("W1")
            .add_node(node)
            .entry_node("n")
            .build()
        )
        workflow2 = (
            WorkflowBuilder("w")
            .description("W2")
            .add_node(node)
            .entry_node("n")
            .build()
        )

        builder = (
            AgentBuilder("test")
            .version("1.0.0")
            .description("Test")
            .add_module(module)
            .add_workflow(workflow1)
        )

        with pytest.raises(DuplicateNameError) as exc_info:
            builder.add_workflow(workflow2)

        assert exc_info.value.entity_type == "workflow"
        assert exc_info.value.name == "w"
