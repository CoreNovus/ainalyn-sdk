"""Unit tests for SchemaValidator."""

from __future__ import annotations

from ainalyn.adapters.outbound.schema_validator import SchemaValidator
from ainalyn.domain.entities import (
    AgentDefinition,
    Module,
    Node,
    NodeType,
    Prompt,
    Tool,
    Workflow,
)
from ainalyn.application.ports.inbound.validate_agent_definition import Severity


class TestSchemaValidatorAgentLevel:
    """Tests for agent-level validation."""

    def test_valid_agent(self) -> None:
        """Test that a valid agent passes validation."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test-agent",
            version="1.0.0",
            description="Test agent",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert len(errors) == 0

    def test_missing_agent_name(self) -> None:
        """Test that missing agent name is detected."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_AGENT_NAME" for e in errors)
        assert any(e.path == "agent.name" for e in errors)
        assert any(e.severity == Severity.ERROR for e in errors)

    def test_invalid_agent_name(self) -> None:
        """Test that invalid agent name is detected."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="Invalid Name",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "INVALID_AGENT_NAME" for e in errors)
        assert any("Invalid Name" in e.message for e in errors)

    def test_missing_agent_version(self) -> None:
        """Test that missing version is detected."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_AGENT_VERSION" for e in errors)

    def test_invalid_agent_version(self) -> None:
        """Test that invalid version format is detected."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="invalid",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "INVALID_AGENT_VERSION" for e in errors)
        assert any("semantic versioning" in e.message for e in errors)

    def test_missing_agent_description(self) -> None:
        """Test that missing description is detected."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_AGENT_DESCRIPTION" for e in errors)

    def test_missing_workflows(self) -> None:
        """Test that missing workflows is detected."""
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_WORKFLOWS" for e in errors)


class TestSchemaValidatorWorkflowLevel:
    """Tests for workflow-level validation."""

    def test_missing_workflow_name(self) -> None:
        """Test that missing workflow name is detected."""
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("", "Description", (node,), "n")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_WORKFLOW_NAME" for e in errors)

    def test_invalid_workflow_name(self) -> None:
        """Test that invalid workflow name is detected."""
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("Invalid Name", "Description", (node,), "n")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "INVALID_WORKFLOW_NAME" for e in errors)

    def test_missing_workflow_description(self) -> None:
        """Test that missing workflow description is detected."""
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "", (node,), "n")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_WORKFLOW_DESCRIPTION" for e in errors)

    def test_missing_workflow_nodes(self) -> None:
        """Test that missing workflow nodes is detected."""
        workflow = Workflow("main", "Main", (), "")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_WORKFLOW_NODES" for e in errors)

    def test_missing_entry_node(self) -> None:
        """Test that missing entry_node is detected."""
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_ENTRY_NODE" for e in errors)

    def test_invalid_entry_node(self) -> None:
        """Test that invalid entry_node reference is detected."""
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "nonexistent")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "INVALID_ENTRY_NODE" for e in errors)
        assert any("nonexistent" in e.message for e in errors)


class TestSchemaValidatorNodeLevel:
    """Tests for node-level validation."""

    def test_missing_node_name(self) -> None:
        """Test that missing node name is detected."""
        node = Node("", "Description", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_NODE_NAME" for e in errors)

    def test_invalid_node_name(self) -> None:
        """Test that invalid node name is detected."""
        node = Node("Invalid Name", "Description", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "Invalid Name")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "INVALID_NODE_NAME" for e in errors)

    def test_missing_node_description(self) -> None:
        """Test that missing node description is detected."""
        node = Node("n", "", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_NODE_DESCRIPTION" for e in errors)

    def test_missing_node_reference(self) -> None:
        """Test that missing node reference is detected."""
        node = Node("n", "N", NodeType.MODULE, "")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_NODE_REFERENCE" for e in errors)

    def test_undefined_node_reference(self) -> None:
        """Test that undefined node reference in next_nodes is detected."""
        node = Node("n", "N", NodeType.MODULE, "m", next_nodes=("undefined",))
        workflow = Workflow("main", "Main", (node,), "n")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "UNDEFINED_NODE_REFERENCE" for e in errors)
        assert any("undefined" in e.message for e in errors)


class TestSchemaValidatorResourceLevel:
    """Tests for resource-level validation."""

    def test_undefined_module_reference(self) -> None:
        """Test that undefined module reference is detected."""
        node = Node("n", "N", NodeType.MODULE, "undefined-module")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "UNDEFINED_RESOURCE_REFERENCE" for e in errors)
        assert any("undefined-module" in e.message for e in errors)

    def test_undefined_prompt_reference(self) -> None:
        """Test that undefined prompt reference is detected."""
        node = Node("n", "N", NodeType.PROMPT, "undefined-prompt")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "UNDEFINED_RESOURCE_REFERENCE" for e in errors)
        assert any("undefined-prompt" in e.message for e in errors)

    def test_undefined_tool_reference(self) -> None:
        """Test that undefined tool reference is detected."""
        node = Node("n", "N", NodeType.TOOL, "undefined-tool")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "UNDEFINED_RESOURCE_REFERENCE" for e in errors)
        assert any("undefined-tool" in e.message for e in errors)

    def test_missing_module_name(self) -> None:
        """Test that missing module name is detected."""
        module = Module("", "Description")
        node = Node("n", "N", NodeType.MODULE, "")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_MODULE_NAME" for e in errors)

    def test_invalid_module_name(self) -> None:
        """Test that invalid module name is detected."""
        module = Module("Invalid Name", "Description")
        node = Node("n", "N", NodeType.MODULE, "Invalid Name")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "INVALID_MODULE_NAME" for e in errors)

    def test_missing_module_description(self) -> None:
        """Test that missing module description is detected."""
        module = Module("m", "")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_MODULE_DESCRIPTION" for e in errors)

    def test_missing_prompt_template(self) -> None:
        """Test that missing prompt template is detected."""
        prompt = Prompt("p", "Description", "")
        node = Node("n", "N", NodeType.PROMPT, "p")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            prompts=(prompt,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_PROMPT_TEMPLATE" for e in errors)

    def test_missing_tool_description(self) -> None:
        """Test that missing tool description is detected."""
        tool = Tool("t", "")
        node = Node("n", "N", NodeType.TOOL, "t")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            tools=(tool,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        assert any(e.code == "MISSING_TOOL_DESCRIPTION" for e in errors)


class TestSchemaValidatorMultipleErrors:
    """Tests for detecting multiple errors."""

    def test_multiple_errors_detected(self) -> None:
        """Test that multiple errors are detected in one pass."""
        # Agent with multiple issues
        node = Node("", "", NodeType.MODULE, "")  # Missing name, description, reference
        workflow = Workflow("", "", (node,), "")  # Missing name, description, entry
        agent = AgentDefinition(
            name="",
            version="",
            description="",
            workflows=(workflow,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        # Should detect multiple errors
        assert len(errors) > 5
        assert any(e.code == "MISSING_AGENT_NAME" for e in errors)
        assert any(e.code == "MISSING_AGENT_VERSION" for e in errors)
        assert any(e.code == "MISSING_AGENT_DESCRIPTION" for e in errors)

    def test_jsonpath_style_paths(self) -> None:
        """Test that error paths use JSONPath-style notation."""
        node = Node("n", "", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        module = Module("m", "M")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        errors = validator.validate_schema(agent)

        # Check JSONPath-style paths
        assert any("agent.workflows[0].nodes[0]" in e.path for e in errors)
