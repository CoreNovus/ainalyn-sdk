"""Unit tests for domain entities."""

from __future__ import annotations

import pytest

from ainalyn.domain.entities import (
    AgentDefinition,
    Module,
    Node,
    NodeType,
    Prompt,
    Tool,
    Workflow,
)


class TestModule:
    """Tests for Module entity."""

    def test_create_module(self) -> None:
        """Test creating a Module entity."""
        module = Module(
            name="http-fetcher",
            description="Fetches data from HTTP endpoints",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )

        assert module.name == "http-fetcher"
        assert module.description == "Fetches data from HTTP endpoints"
        assert module.input_schema == {"type": "object"}
        assert module.output_schema == {"type": "object"}

    def test_module_is_immutable(self) -> None:
        """Test that Module is immutable."""
        module = Module(name="test", description="Test")

        with pytest.raises(AttributeError):
            module.name = "new-name"  # type: ignore[misc]

    def test_module_default_schemas(self) -> None:
        """Test that schemas default to empty dict."""
        module = Module(name="test", description="Test")

        assert module.input_schema == {}
        assert module.output_schema == {}


class TestPrompt:
    """Tests for Prompt entity."""

    def test_create_prompt(self) -> None:
        """Test creating a Prompt entity."""
        prompt = Prompt(
            name="analyzer",
            description="Analyzes data",
            template="Analyze: {{data}}",
            variables=("data",),
        )

        assert prompt.name == "analyzer"
        assert prompt.description == "Analyzes data"
        assert prompt.template == "Analyze: {{data}}"
        assert prompt.variables == ("data",)

    def test_prompt_is_immutable(self) -> None:
        """Test that Prompt is immutable."""
        prompt = Prompt(name="test", description="Test", template="T")

        with pytest.raises(AttributeError):
            prompt.name = "new-name"  # type: ignore[misc]

    def test_prompt_default_variables(self) -> None:
        """Test that variables default to empty tuple."""
        prompt = Prompt(name="test", description="Test", template="T")

        assert prompt.variables == ()


class TestTool:
    """Tests for Tool entity."""

    def test_create_tool(self) -> None:
        """Test creating a Tool entity."""
        tool = Tool(
            name="file-writer",
            description="Writes files",
            input_schema={"type": "object"},
            output_schema={"type": "boolean"},
        )

        assert tool.name == "file-writer"
        assert tool.description == "Writes files"
        assert tool.input_schema == {"type": "object"}
        assert tool.output_schema == {"type": "boolean"}

    def test_tool_is_immutable(self) -> None:
        """Test that Tool is immutable."""
        tool = Tool(name="test", description="Test")

        with pytest.raises(AttributeError):
            tool.name = "new-name"  # type: ignore[misc]


class TestNode:
    """Tests for Node entity."""

    def test_create_node_with_module(self) -> None:
        """Test creating a Node that references a module."""
        node = Node(
            name="fetch",
            description="Fetch data",
            node_type=NodeType.MODULE,
            reference="http-fetcher",
            inputs=("url",),
            outputs=("data",),
            next_nodes=("process",),
        )

        assert node.name == "fetch"
        assert node.description == "Fetch data"
        assert node.node_type == NodeType.MODULE
        assert node.reference == "http-fetcher"
        assert node.inputs == ("url",)
        assert node.outputs == ("data",)
        assert node.next_nodes == ("process",)

    def test_create_node_with_prompt(self) -> None:
        """Test creating a Node that references a prompt."""
        node = Node(
            name="analyze",
            description="Analyze",
            node_type=NodeType.PROMPT,
            reference="analyzer",
        )

        assert node.node_type == NodeType.PROMPT
        assert node.reference == "analyzer"

    def test_create_node_with_tool(self) -> None:
        """Test creating a Node that references a tool."""
        node = Node(
            name="write",
            description="Write",
            node_type=NodeType.TOOL,
            reference="file-writer",
        )

        assert node.node_type == NodeType.TOOL
        assert node.reference == "file-writer"

    def test_node_is_immutable(self) -> None:
        """Test that Node is immutable."""
        node = Node(
            name="test",
            description="Test",
            node_type=NodeType.MODULE,
            reference="test-module",
        )

        with pytest.raises(AttributeError):
            node.name = "new-name"  # type: ignore[misc]

    def test_node_default_values(self) -> None:
        """Test Node default values."""
        node = Node(
            name="test",
            description="Test",
            node_type=NodeType.MODULE,
            reference="test-module",
        )

        assert node.inputs == ()
        assert node.outputs == ()
        assert node.next_nodes == ()


class TestWorkflow:
    """Tests for Workflow entity."""

    def test_create_workflow(self) -> None:
        """Test creating a Workflow entity."""
        node = Node(
            name="fetch",
            description="Fetch",
            node_type=NodeType.MODULE,
            reference="http-fetcher",
        )

        workflow = Workflow(
            name="main",
            description="Main workflow",
            nodes=(node,),
            entry_node="fetch",
        )

        assert workflow.name == "main"
        assert workflow.description == "Main workflow"
        assert len(workflow.nodes) == 1
        assert workflow.entry_node == "fetch"

    def test_workflow_is_immutable(self) -> None:
        """Test that Workflow is immutable."""
        node = Node(
            name="test",
            description="Test",
            node_type=NodeType.MODULE,
            reference="test",
        )
        workflow = Workflow(
            name="test",
            description="Test",
            nodes=(node,),
            entry_node="test",
        )

        with pytest.raises(AttributeError):
            workflow.name = "new-name"  # type: ignore[misc]


class TestAgentDefinition:
    """Tests for AgentDefinition entity (Aggregate Root)."""

    def test_create_minimal_agent(self) -> None:
        """Test creating a minimal AgentDefinition."""
        node = Node(
            name="n",
            description="N",
            node_type=NodeType.MODULE,
            reference="m",
        )
        workflow = Workflow(
            name="main",
            description="Main",
            nodes=(node,),
            entry_node="n",
        )
        module = Module(name="m", description="M")

        agent = AgentDefinition(
            name="my-agent",
            version="1.0.0",
            description="My agent",
            workflows=(workflow,),
            modules=(module,),
        )

        assert agent.name == "my-agent"
        assert agent.version == "1.0.0"
        assert agent.description == "My agent"
        assert len(agent.workflows) == 1
        assert len(agent.modules) == 1
        assert agent.prompts == ()
        assert agent.tools == ()

    def test_create_full_agent(self) -> None:
        """Test creating an AgentDefinition with all resources."""
        module = Module(name="m", description="M")
        prompt = Prompt(name="p", description="P", template="T")
        tool = Tool(name="t", description="T")

        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.PROMPT, "p", next_nodes=("n3",))
        node3 = Node("n3", "N3", NodeType.TOOL, "t")

        workflow = Workflow(
            name="main",
            description="Main",
            nodes=(node1, node2, node3),
            entry_node="n1",
        )

        agent = AgentDefinition(
            name="my-agent",
            version="1.0.0",
            description="My agent",
            workflows=(workflow,),
            modules=(module,),
            prompts=(prompt,),
            tools=(tool,),
        )

        assert len(agent.modules) == 1
        assert len(agent.prompts) == 1
        assert len(agent.tools) == 1
        assert len(agent.workflows) == 1

    def test_agent_is_immutable(self) -> None:
        """Test that AgentDefinition is immutable."""
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("w", "W", (node,), "n")
        module = Module("m", "M")

        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        with pytest.raises(AttributeError):
            agent.name = "new-name"  # type: ignore[misc]

    def test_agent_default_resources(self) -> None:
        """Test AgentDefinition default resource values."""
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("w", "W", (node,), "n")
        module = Module("m", "M")

        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        assert agent.prompts == ()
        assert agent.tools == ()


class TestNodeType:
    """Tests for NodeType enum."""

    def test_node_type_values(self) -> None:
        """Test NodeType enum values."""
        assert NodeType.MODULE.value == "module"
        assert NodeType.PROMPT.value == "prompt"
        assert NodeType.TOOL.value == "tool"

    def test_node_type_members(self) -> None:
        """Test NodeType has expected members."""
        assert hasattr(NodeType, "MODULE")
        assert hasattr(NodeType, "PROMPT")
        assert hasattr(NodeType, "TOOL")
