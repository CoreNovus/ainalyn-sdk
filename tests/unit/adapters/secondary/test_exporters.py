"""Unit tests for YamlExporter."""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from ainalyn.adapters.outbound.yaml_serializer import YamlExporter
from ainalyn.domain.entities import (
    AgentDefinition,
    Module,
    Node,
    NodeType,
    Prompt,
    Tool,
    Workflow,
)


class TestYamlExporterExport:
    """Tests for YAML export functionality."""

    def test_export_minimal_agent(self) -> None:
        """Test exporting a minimal agent definition."""
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

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)

        # Verify it's valid YAML
        data = yaml.safe_load(yaml_content)
        assert data["name"] == "test-agent"
        assert data["version"] == "1.0.0"
        assert data["description"] == "Test agent"

    def test_export_includes_all_agent_fields(self) -> None:
        """Test that all agent-level fields are exported."""
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

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)
        data = yaml.safe_load(yaml_content)

        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "workflows" in data
        assert "modules" in data

    def test_export_workflow_structure(self) -> None:
        """Test that workflow structure is correctly exported."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main workflow", (node1, node2), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)
        data = yaml.safe_load(yaml_content)

        wf = data["workflows"][0]
        assert wf["name"] == "main"
        assert wf["description"] == "Main workflow"
        assert wf["entry_node"] == "n1"
        assert len(wf["nodes"]) == 2

    def test_export_node_structure(self) -> None:
        """Test that node structure is correctly exported."""
        module = Module("m", "M")
        node = Node(
            "n",
            "N",
            NodeType.MODULE,
            "m",
            next_nodes=("n2",),
            inputs=("input1",),
            outputs=("output1",),
        )
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)
        data = yaml.safe_load(yaml_content)

        node_data = data["workflows"][0]["nodes"][0]
        assert node_data["name"] == "n"
        assert node_data["description"] == "N"
        assert node_data["type"] == "module"
        assert node_data["reference"] == "m"
        assert node_data["next_nodes"] == ["n2"]
        assert node_data["inputs"] == ["input1"]
        assert node_data["outputs"] == ["output1"]

    def test_export_module_with_schemas(self) -> None:
        """Test that modules with schemas are correctly exported."""
        module = Module(
            "m",
            "M",
            input_schema={"type": "object"},
            output_schema={"type": "string"},
        )
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)
        data = yaml.safe_load(yaml_content)

        module_data = data["modules"][0]
        assert module_data["name"] == "m"
        assert module_data["description"] == "M"
        assert module_data["input_schema"] == {"type": "object"}
        assert module_data["output_schema"] == {"type": "string"}

    def test_export_prompt_with_variables(self) -> None:
        """Test that prompts with variables are correctly exported."""
        module = Module("m", "M")
        prompt = Prompt("p", "P", "Template", variables=("var1", "var2"))
        node1 = Node("n1", "N1", NodeType.MODULE, "m")
        node2 = Node("n2", "N2", NodeType.PROMPT, "p")
        workflow = Workflow("main", "Main", (node1, node2), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
            prompts=(prompt,),
        )

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)
        data = yaml.safe_load(yaml_content)

        prompt_data = data["prompts"][0]
        assert prompt_data["name"] == "p"
        assert prompt_data["description"] == "P"
        assert prompt_data["template"] == "Template"
        assert prompt_data["variables"] == ["var1", "var2"]

    def test_export_tool_with_parameters(self) -> None:
        """Test that tools with parameters are correctly exported."""
        module = Module("m", "M")
        tool = Tool(
            "t",
            "T",
            input_schema={"type": "object"},
            output_schema={"type": "string"},
        )
        node1 = Node("n1", "N1", NodeType.MODULE, "m")
        node2 = Node("n2", "N2", NodeType.TOOL, "t")
        workflow = Workflow("main", "Main", (node1, node2), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
            tools=(tool,),
        )

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)
        data = yaml.safe_load(yaml_content)

        tool_data = data["tools"][0]
        assert tool_data["name"] == "t"
        assert tool_data["description"] == "T"
        assert tool_data["input_schema"] == {"type": "object"}
        assert tool_data["output_schema"] == {"type": "string"}

    def test_export_unicode_content(self) -> None:
        """Test that Unicode content is correctly exported."""
        module = Module("m", "測試模組")
        node = Node("n", "測試節點", NodeType.MODULE, "m")
        workflow = Workflow("main", "主要工作流程", (node,), "n")
        agent = AgentDefinition(
            name="test-agent",
            version="1.0.0",
            description="這是一個測試代理",
            workflows=(workflow,),
            modules=(module,),
        )

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)
        data = yaml.safe_load(yaml_content)

        assert data["description"] == "這是一個測試代理"
        assert data["workflows"][0]["description"] == "主要工作流程"
        assert data["modules"][0]["description"] == "測試模組"

    def test_export_multiple_workflows(self) -> None:
        """Test exporting agent with multiple workflows."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m")
        node2 = Node("n2", "N2", NodeType.MODULE, "m")
        workflow1 = Workflow("wf1", "WF1", (node1,), "n1")
        workflow2 = Workflow("wf2", "WF2", (node2,), "n2")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow1, workflow2),
            modules=(module,),
        )

        exporter = YamlExporter()
        yaml_content = exporter.export(agent)
        data = yaml.safe_load(yaml_content)

        assert len(data["workflows"]) == 2
        assert data["workflows"][0]["name"] == "wf1"
        assert data["workflows"][1]["name"] == "wf2"


class TestYamlExporterWrite:
    """Tests for file writing functionality."""

    def test_write_creates_file(self) -> None:
        """Test that write creates a file with content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            exporter = YamlExporter()
            content = "test: content"

            exporter.write(content, path)

            assert path.exists()
            assert path.read_text(encoding="utf-8") == content

    def test_write_creates_parent_directories(self) -> None:
        """Test that write creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "nested" / "test.yaml"
            exporter = YamlExporter()
            content = "test: content"

            exporter.write(content, path)

            assert path.exists()
            assert path.read_text(encoding="utf-8") == content

    def test_write_unicode_content(self) -> None:
        """Test writing Unicode content to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            exporter = YamlExporter()
            content = "test: 測試內容"

            exporter.write(content, path)

            assert path.exists()
            written_content = path.read_text(encoding="utf-8")
            assert written_content == content

    def test_write_overwrites_existing_file(self) -> None:
        """Test that write overwrites existing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            exporter = YamlExporter()

            # Write first time
            exporter.write("first: content", path)
            assert path.read_text(encoding="utf-8") == "first: content"

            # Overwrite
            exporter.write("second: content", path)
            assert path.read_text(encoding="utf-8") == "second: content"


class TestYamlExporterIntegration:
    """Integration tests for export and write together."""

    def test_export_and_write_minimal_agent(self) -> None:
        """Test complete export and write workflow."""
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
            path = Path(tmpdir) / "agent.yaml"
            exporter = YamlExporter()

            # Export and write
            yaml_content = exporter.export(agent)
            exporter.write(yaml_content, path)

            # Verify file content
            written_data = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert written_data["name"] == "test-agent"
            assert written_data["version"] == "1.0.0"

    def test_export_complex_agent_to_file(self) -> None:
        """Test exporting a complex agent with all resource types."""
        module = Module("m", "M")
        prompt = Prompt("p", "P", "Template")
        tool = Tool("t", "T")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.PROMPT, "p", next_nodes=("n3",))
        node3 = Node("n3", "N3", NodeType.TOOL, "t")
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="complex-agent",
            version="1.0.0",
            description="Complex test agent",
            workflows=(workflow,),
            modules=(module,),
            prompts=(prompt,),
            tools=(tool,),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "complex.yaml"
            exporter = YamlExporter()

            yaml_content = exporter.export(agent)
            exporter.write(yaml_content, path)

            # Verify all sections exist
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert "workflows" in data
            assert "modules" in data
            assert "prompts" in data
            assert "tools" in data
            assert len(data["workflows"][0]["nodes"]) == 3
