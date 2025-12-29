"""End-to-end integration tests for the compilation workflow."""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from ainalyn.domain.entities import (
    AgentDefinition,
    Module,
    Node,
    NodeType,
    Prompt,
    Tool,
    Workflow,
)
from ainalyn.infrastructure import create_default_service


class TestEndToEndCompilation:
    """End-to-end tests for the complete compilation workflow."""

    def test_simple_agent_compilation(self) -> None:
        """Test compiling a simple agent from start to finish."""
        # Create a simple agent
        module = Module("http-fetch", "HTTP fetcher module")
        node = Node(
            "fetch",
            "Fetch data from API",
            NodeType.MODULE,
            "http-fetch",
            outputs=("data",),
        )
        workflow = Workflow("main", "Main workflow", (node,), "fetch")
        agent = AgentDefinition(
            name="api-fetcher",
            version="1.0.0",
            description="Simple API fetching agent",
            workflows=(workflow,),
            modules=(module,),
        )

        # Compile using DefinitionService
        service = create_default_service()
        result = service.compile(agent)

        # Verify compilation succeeded
        assert result.is_successful
        assert result.validation_result.is_valid
        assert result.yaml_content is not None

        # Verify YAML structure
        data = yaml.safe_load(result.yaml_content)
        assert data["name"] == "api-fetcher"
        assert data["version"] == "1.0.0"
        assert len(data["workflows"]) == 1
        assert len(data["modules"]) == 1

    def test_complex_agent_compilation(self) -> None:
        """Test compiling a complex agent with all resource types."""
        # Create resources
        module = Module("processor", "Data processor")
        prompt = Prompt("analyzer", "Analyze data", "Analyze: {data}")
        tool = Tool("writer", "Write results")

        # Create nodes
        node1 = Node(
            "process",
            "Process input",
            NodeType.MODULE,
            "processor",
            next_nodes=("analyze",),
        )
        node2 = Node(
            "analyze",
            "Analyze processed data",
            NodeType.PROMPT,
            "analyzer",
            next_nodes=("write",),
        )
        node3 = Node(
            "write",
            "Write final results",
            NodeType.TOOL,
            "writer",
            outputs=("result",),
        )

        # Create workflow
        workflow = Workflow(
            "pipeline",
            "Data processing pipeline",
            (node1, node2, node3),
            "process",
        )

        # Create agent
        agent = AgentDefinition(
            name="data-pipeline",
            version="2.0.0",
            description="Complete data processing pipeline",
            workflows=(workflow,),
            modules=(module,),
            prompts=(prompt,),
            tools=(tool,),
        )

        # Compile
        service = create_default_service()
        result = service.compile(agent)

        # Verify
        assert result.is_successful
        data = yaml.safe_load(result.yaml_content)
        assert "modules" in data
        assert "prompts" in data
        assert "tools" in data
        assert len(data["workflows"][0]["nodes"]) == 3

    def test_unicode_agent_compilation(self) -> None:
        """Test compiling an agent with Unicode content."""
        module = Module("processor", "數據處理模組")
        node = Node("node", "處理節點", NodeType.MODULE, "processor", outputs=("result",))
        workflow = Workflow("main", "主要工作流程", (node,), "node")
        agent = AgentDefinition(
            name="unicode-agent",
            version="1.0.0",
            description="支持 Unicode 的代理",
            workflows=(workflow,),
            modules=(module,),
        )

        service = create_default_service()
        result = service.compile(agent)

        assert result.is_successful
        data = yaml.safe_load(result.yaml_content)
        assert data["description"] == "支持 Unicode 的代理"
        assert data["workflows"][0]["description"] == "主要工作流程"

    def test_invalid_agent_compilation(self) -> None:
        """Test that invalid agents fail compilation gracefully."""
        # Create agent with invalid name
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="Invalid Name",  # Invalid: contains spaces
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        service = create_default_service()
        result = service.compile(agent)

        # Should fail validation
        assert not result.is_successful
        assert not result.validation_result.is_valid
        assert result.yaml_content is None
        assert any(e.code == "INVALID_AGENT_NAME" for e in result.validation_result.errors)

    def test_agent_with_warnings_compiles(self) -> None:
        """Test that agents with warnings still compile successfully."""
        module1 = Module("m1", "M1")
        module2 = Module("m2", "M2")  # Unused - will generate warning
        node = Node("n", "N", NodeType.MODULE, "m1")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module1, module2),
        )

        service = create_default_service()
        result = service.compile(agent)

        # Should succeed despite warnings
        assert result.is_successful
        assert result.validation_result.is_valid
        assert result.validation_result.has_warnings
        assert result.yaml_content is not None


class TestEndToEndFileExport:
    """End-to-end tests for file export workflow."""

    def test_compile_to_file(self) -> None:
        """Test complete workflow from definition to file."""
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

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "agent.yaml"
            service = create_default_service()

            result = service.compile_to_file(agent, output_path)

            # Verify result
            assert result.is_successful
            assert result.output_path == output_path

            # Verify file
            assert output_path.exists()
            data = yaml.safe_load(output_path.read_text(encoding="utf-8"))
            assert data["name"] == "test-agent"

    def test_compile_to_nested_path(self) -> None:
        """Test compiling to a nested directory path."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test-agent",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "agents" / "v1" / "agent.yaml"
            service = create_default_service()

            result = service.compile_to_file(agent, output_path)

            assert result.is_successful
            assert output_path.exists()
            assert output_path.parent.exists()

    def test_invalid_agent_no_file_created(self) -> None:
        """Test that no file is created for invalid agents."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="",  # Invalid
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "agent.yaml"
            service = create_default_service()

            result = service.compile_to_file(agent, output_path)

            assert not result.is_successful
            assert not output_path.exists()


class TestDefinitionServiceAPI:
    """Tests for DefinitionService public API."""

    def test_validate_method(self) -> None:
        """Test the validate method."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m", outputs=("result",))
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        service = create_default_service()
        result = service.validate(agent)

        assert result.is_valid

    def test_export_method(self) -> None:
        """Test the export method."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        service = create_default_service()
        yaml_content = service.export(agent)

        assert isinstance(yaml_content, str)
        assert "name: test" in yaml_content

    def test_export_to_file_method(self) -> None:
        """Test the export_to_file method."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            service = create_default_service()

            service.export_to_file(agent, path)

            assert path.exists()
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert data["name"] == "test"

    def test_compile_method(self) -> None:
        """Test the compile method."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        service = create_default_service()
        result = service.compile(agent)

        assert result.is_successful
        assert result.validation_result.is_valid
        assert result.yaml_content is not None

    def test_compile_to_file_method(self) -> None:
        """Test the compile_to_file method."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            service = create_default_service()

            result = service.compile_to_file(agent, path)

            assert result.is_successful
            assert result.output_path == path
            assert path.exists()
