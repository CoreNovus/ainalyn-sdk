"""Unit tests for application use cases."""

from __future__ import annotations

import tempfile
from pathlib import Path

from ainalyn.adapters.outbound.static_analyzer import StaticAnalyzer
from ainalyn.adapters.outbound.yaml_serializer import YamlExporter
from ainalyn.adapters.outbound.schema_validator import SchemaValidator
from ainalyn.application.use_cases.compile_definition import CompileDefinitionUseCase
from ainalyn.application.use_cases.export_definition import ExportDefinitionUseCase
from ainalyn.application.use_cases.validate_definition import ValidateDefinitionUseCase
from ainalyn.domain.entities import (
    AgentDefinition,
    Module,
    Node,
    NodeType,
    Workflow,
)


class TestValidateDefinitionUseCase:
    """Tests for ValidateDefinitionUseCase."""

    def test_validate_valid_definition(self) -> None:
        """Test validating a valid definition."""
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

        validator = SchemaValidator()
        analyzer = StaticAnalyzer()
        use_case = ValidateDefinitionUseCase(validator, analyzer)

        result = use_case.execute(agent)

        assert result.is_valid

    def test_validate_invalid_definition(self) -> None:
        """Test validating an invalid definition."""
        module = Module("m", "M")
        node = Node("n", "N", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="",  # Invalid: empty name
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        validator = SchemaValidator()
        analyzer = StaticAnalyzer()
        use_case = ValidateDefinitionUseCase(validator, analyzer)

        result = use_case.execute(agent)

        assert not result.is_valid
        assert len(result.errors) > 0
        assert any(e.code == "MISSING_AGENT_NAME" for e in result.errors)

    def test_static_analysis_skipped_on_schema_errors(self) -> None:
        """Test that static analysis is skipped if schema has errors."""
        module1 = Module("m1", "M1")
        module2 = Module("m2", "M2")  # Unused
        node = Node("n", "N", NodeType.MODULE, "m1")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="",  # Schema error
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module1, module2),  # Would trigger unused warning
        )

        validator = SchemaValidator()
        analyzer = StaticAnalyzer()
        use_case = ValidateDefinitionUseCase(validator, analyzer)

        result = use_case.execute(agent)

        # Should have schema error but no static analysis warnings
        assert not result.is_valid
        assert any(e.code == "MISSING_AGENT_NAME" for e in result.errors)
        assert not any(e.code == "UNUSED_MODULE" for e in result.errors)

    def test_static_analysis_runs_on_schema_warnings(self) -> None:
        """Test that static analysis runs if only schema warnings exist."""
        # Note: Current implementation doesn't have schema warnings,
        # so we test that analysis runs on valid schema
        module1 = Module("m1", "M1")
        module2 = Module("m2", "M2")  # Unused - will be detected by analyzer
        node = Node("n", "N", NodeType.MODULE, "m1")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module1, module2),
        )

        validator = SchemaValidator()
        analyzer = StaticAnalyzer()
        use_case = ValidateDefinitionUseCase(validator, analyzer)

        result = use_case.execute(agent)

        # Should be valid (no errors) but have warnings
        assert result.is_valid
        assert result.has_warnings
        assert any(e.code == "UNUSED_MODULE" for e in result.errors)


class TestExportDefinitionUseCase:
    """Tests for ExportDefinitionUseCase."""

    def test_execute_returns_yaml_string(self) -> None:
        """Test that execute returns YAML string."""
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

        exporter = YamlExporter()
        use_case = ExportDefinitionUseCase(exporter)

        result = use_case.execute(agent)

        assert isinstance(result, str)
        assert "name: test" in result
        assert "version: 1.0.0" in result

    def test_execute_to_file_creates_file(self) -> None:
        """Test that execute_to_file creates a file."""
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
            exporter = YamlExporter()
            use_case = ExportDefinitionUseCase(exporter)

            use_case.execute_to_file(agent, path)

            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "name: test" in content


class TestCompileDefinitionUseCase:
    """Tests for CompileDefinitionUseCase."""

    def test_compile_valid_definition(self) -> None:
        """Test compiling a valid definition."""
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

        validator = ValidateDefinitionUseCase(SchemaValidator(), StaticAnalyzer())
        exporter = ExportDefinitionUseCase(YamlExporter())
        use_case = CompileDefinitionUseCase(validator, exporter)

        result = use_case.execute(agent)

        assert result.is_successful
        assert result.validation_result.is_valid
        assert result.yaml_content is not None
        assert "name: test" in result.yaml_content

    def test_compile_invalid_definition(self) -> None:
        """Test compiling an invalid definition."""
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

        validator = ValidateDefinitionUseCase(SchemaValidator(), StaticAnalyzer())
        exporter = ExportDefinitionUseCase(YamlExporter())
        use_case = CompileDefinitionUseCase(validator, exporter)

        result = use_case.execute(agent)

        assert not result.is_successful
        assert not result.validation_result.is_valid
        assert result.yaml_content is None

    def test_compile_to_file_valid_definition(self) -> None:
        """Test compiling a valid definition to file."""
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
            validator = ValidateDefinitionUseCase(SchemaValidator(), StaticAnalyzer())
            exporter = ExportDefinitionUseCase(YamlExporter())
            use_case = CompileDefinitionUseCase(validator, exporter)

            result = use_case.execute_to_file(agent, path)

            assert result.is_successful
            assert result.output_path == path
            assert path.exists()

    def test_compile_to_file_invalid_definition(self) -> None:
        """Test compiling an invalid definition to file."""
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
            path = Path(tmpdir) / "test.yaml"
            validator = ValidateDefinitionUseCase(SchemaValidator(), StaticAnalyzer())
            exporter = ExportDefinitionUseCase(YamlExporter())
            use_case = CompileDefinitionUseCase(validator, exporter)

            result = use_case.execute_to_file(agent, path)

            assert not result.is_successful
            assert result.output_path is None
            assert not path.exists()  # File should not be created

    def test_compilation_result_properties(self) -> None:
        """Test CompilationResult properties."""
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

        validator = ValidateDefinitionUseCase(SchemaValidator(), StaticAnalyzer())
        exporter = ExportDefinitionUseCase(YamlExporter())
        use_case = CompileDefinitionUseCase(validator, exporter)

        result = use_case.execute(agent)

        # Test is_successful property
        assert result.is_successful
        assert result.validation_result.is_valid
        assert result.yaml_content is not None

    def test_compile_with_warnings(self) -> None:
        """Test compiling a definition with warnings."""
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

        validator = ValidateDefinitionUseCase(SchemaValidator(), StaticAnalyzer())
        exporter = ExportDefinitionUseCase(YamlExporter())
        use_case = CompileDefinitionUseCase(validator, exporter)

        result = use_case.execute(agent)

        # Should be successful despite warnings
        assert result.is_successful
        assert result.validation_result.is_valid
        assert result.validation_result.has_warnings
        assert result.yaml_content is not None
