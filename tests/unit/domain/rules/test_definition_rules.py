"""Unit tests for domain rules."""

from __future__ import annotations

from ainalyn.domain.entities import AgentDefinition, Module, Node, NodeType, Workflow
from ainalyn.domain.rules import DefinitionRules


class TestNameValidation:
    """Tests for name validation rules."""

    def test_valid_names(self) -> None:
        """Test that valid names pass validation."""
        assert DefinitionRules.is_valid_name("my-agent")
        assert DefinitionRules.is_valid_name("http-fetcher")
        assert DefinitionRules.is_valid_name("data-processor-v2")
        assert DefinitionRules.is_valid_name("a")
        assert DefinitionRules.is_valid_name("a1")
        assert DefinitionRules.is_valid_name("agent-123")

    def test_invalid_names(self) -> None:
        """Test that invalid names fail validation."""
        # Empty string
        assert not DefinitionRules.is_valid_name("")

        # Uppercase letters
        assert not DefinitionRules.is_valid_name("MyAgent")
        assert not DefinitionRules.is_valid_name("HTTP-Fetcher")

        # Spaces
        assert not DefinitionRules.is_valid_name("my agent")
        assert not DefinitionRules.is_valid_name("http fetcher")

        # Underscores
        assert not DefinitionRules.is_valid_name("my_agent")

        # Starting with number
        assert not DefinitionRules.is_valid_name("123-agent")

        # Starting with hyphen
        assert not DefinitionRules.is_valid_name("-agent")

        # Special characters
        assert not DefinitionRules.is_valid_name("my@agent")
        assert not DefinitionRules.is_valid_name("my.agent")


class TestVersionValidation:
    """Tests for version validation rules."""

    def test_valid_versions(self) -> None:
        """Test that valid versions pass validation."""
        assert DefinitionRules.is_valid_version("1.0.0")
        assert DefinitionRules.is_valid_version("0.1.0")
        assert DefinitionRules.is_valid_version("10.20.30")
        assert DefinitionRules.is_valid_version("1.0.0-alpha")
        assert DefinitionRules.is_valid_version("1.0.0-alpha.1")
        assert DefinitionRules.is_valid_version("1.0.0+build.123")
        assert DefinitionRules.is_valid_version("1.0.0-beta+build")

    def test_invalid_versions(self) -> None:
        """Test that invalid versions fail validation."""
        # Empty string
        assert not DefinitionRules.is_valid_version("")

        # Missing patch
        assert not DefinitionRules.is_valid_version("1.0")

        # Missing minor
        assert not DefinitionRules.is_valid_version("1")

        # With 'v' prefix
        assert not DefinitionRules.is_valid_version("v1.0.0")

        # Invalid format
        assert not DefinitionRules.is_valid_version("1.0.0.0")
        assert not DefinitionRules.is_valid_version("a.b.c")


class TestWorkflowValidation:
    """Tests for workflow validation rules."""

    def test_workflow_has_valid_entry(self) -> None:
        """Test validation of workflow entry node."""
        node = Node("fetch", "Fetch", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "fetch")

        assert DefinitionRules.workflow_has_valid_entry(workflow)

    def test_workflow_invalid_entry_node(self) -> None:
        """Test workflow with invalid entry node."""
        node = Node("fetch", "Fetch", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "nonexistent")

        assert not DefinitionRules.workflow_has_valid_entry(workflow)

    def test_workflow_empty_entry_node(self) -> None:
        """Test workflow with empty entry node."""
        node = Node("fetch", "Fetch", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "")

        assert not DefinitionRules.workflow_has_valid_entry(workflow)

    def test_workflow_has_nodes(self) -> None:
        """Test that workflow has nodes."""
        node = Node("fetch", "Fetch", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node,), "fetch")

        assert DefinitionRules.workflow_has_nodes(workflow)

    def test_workflow_empty_nodes(self) -> None:
        """Test workflow with no nodes."""
        workflow = Workflow("main", "Main", (), "")

        assert not DefinitionRules.workflow_has_nodes(workflow)


class TestNodeReferences:
    """Tests for node reference validation."""

    def test_get_undefined_node_references(self) -> None:
        """Test detection of undefined node references."""
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m", next_nodes=("nonexistent",))

        workflow = Workflow("main", "Main", (node1, node2), "n1")

        undefined = DefinitionRules.get_undefined_node_references(workflow)

        assert len(undefined) == 1
        assert ("n2", "nonexistent") in undefined

    def test_no_undefined_node_references(self) -> None:
        """Test workflow with all valid references."""
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")

        workflow = Workflow("main", "Main", (node1, node2), "n1")

        undefined = DefinitionRules.get_undefined_node_references(workflow)

        assert len(undefined) == 0


class TestResourceReferences:
    """Tests for resource reference validation."""

    def test_get_undefined_resource_references(self) -> None:
        """Test detection of undefined resource references."""
        module = Module("m1", "M1")
        node1 = Node("n1", "N1", NodeType.MODULE, "m1", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "undefined-module")

        workflow = Workflow("main", "Main", (node1, node2), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        undefined = DefinitionRules.get_undefined_resource_references(agent)

        assert len(undefined) == 1
        assert ("n2", "module", "undefined-module") in undefined

    def test_no_undefined_resource_references(self) -> None:
        """Test agent with all valid resource references."""
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

        undefined = DefinitionRules.get_undefined_resource_references(agent)

        assert len(undefined) == 0


class TestCircularDependencies:
    """Tests for circular dependency detection."""

    def test_detect_simple_cycle(self) -> None:
        """Test detection of simple circular dependency."""
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m", next_nodes=("n1",))

        workflow = Workflow("main", "Main", (node1, node2), "n1")

        cycles = DefinitionRules.detect_circular_dependencies(workflow)

        assert len(cycles) > 0
        assert "n1" in cycles[0]
        assert "n2" in cycles[0]

    def test_detect_self_reference(self) -> None:
        """Test detection of node referencing itself."""
        node = Node("n", "N", NodeType.MODULE, "m", next_nodes=("n",))

        workflow = Workflow("main", "Main", (node,), "n")

        cycles = DefinitionRules.detect_circular_dependencies(workflow)

        assert len(cycles) > 0
        assert "n" in cycles[0]

    def test_no_circular_dependencies(self) -> None:
        """Test workflow with no circular dependencies."""
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m", next_nodes=("n3",))
        node3 = Node("n3", "N3", NodeType.MODULE, "m")

        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")

        cycles = DefinitionRules.detect_circular_dependencies(workflow)

        assert len(cycles) == 0


class TestUnreachableNodes:
    """Tests for unreachable node detection."""

    def test_get_unreachable_nodes(self) -> None:
        """Test detection of unreachable nodes."""
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")
        node3 = Node("n3", "N3", NodeType.MODULE, "m")  # Unreachable

        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")

        unreachable = DefinitionRules.get_unreachable_nodes(workflow)

        assert len(unreachable) == 1
        assert "n3" in unreachable

    def test_no_unreachable_nodes(self) -> None:
        """Test workflow with all nodes reachable."""
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2", "n3"))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")
        node3 = Node("n3", "N3", NodeType.MODULE, "m")

        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")

        unreachable = DefinitionRules.get_unreachable_nodes(workflow)

        assert len(unreachable) == 0


class TestUnusedResources:
    """Tests for unused resource detection."""

    def test_get_unused_modules(self) -> None:
        """Test detection of unused modules."""
        module1 = Module("m1", "M1")
        module2 = Module("m2", "M2")  # Unused
        node = Node("n", "N", NodeType.MODULE, "m1")
        workflow = Workflow("main", "Main", (node,), "n")

        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module1, module2),
        )

        unused = DefinitionRules.get_unused_resources(agent)

        assert "m2" in unused["modules"]
        assert "m1" not in unused["modules"]

    def test_no_unused_resources(self) -> None:
        """Test agent with all resources used."""
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

        unused = DefinitionRules.get_unused_resources(agent)

        assert len(unused["modules"]) == 0
        assert len(unused["prompts"]) == 0
        assert len(unused["tools"]) == 0
