"""Unit tests for StaticAnalyzer."""

from __future__ import annotations

from ainalyn.adapters.outbound.static_analyzer import StaticAnalyzer
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


class TestStaticAnalyzerCircularDependencies:
    """Tests for circular dependency detection."""

    def test_no_circular_dependencies(self) -> None:
        """Test that valid workflows pass circular dependency check."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node1, node2), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        assert not any(i.code == "CIRCULAR_DEPENDENCY" for i in issues)

    def test_simple_circular_dependency(self) -> None:
        """Test detection of simple circular dependency (A -> B -> A)."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m", next_nodes=("n1",))
        workflow = Workflow("main", "Main", (node1, node2), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        circular_issues = [i for i in issues if i.code == "CIRCULAR_DEPENDENCY"]
        assert len(circular_issues) > 0
        assert any(i.severity == Severity.ERROR for i in circular_issues)
        assert any("n1" in i.message and "n2" in i.message for i in circular_issues)

    def test_self_referencing_node(self) -> None:
        """Test detection of self-referencing node (A -> A)."""
        module = Module("m", "M")
        node = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n1",))
        workflow = Workflow("main", "Main", (node,), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        assert any(i.code == "CIRCULAR_DEPENDENCY" for i in issues)
        assert any("n1" in i.message for i in issues)

    def test_complex_circular_dependency(self) -> None:
        """Test detection of complex circular dependency (A -> B -> C -> A)."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m", next_nodes=("n3",))
        node3 = Node("n3", "N3", NodeType.MODULE, "m", next_nodes=("n1",))
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        assert any(i.code == "CIRCULAR_DEPENDENCY" for i in issues)


class TestStaticAnalyzerUnreachableNodes:
    """Tests for unreachable node detection."""

    def test_all_nodes_reachable(self) -> None:
        """Test that all nodes reachable from entry pass check."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2", "n3"))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")
        node3 = Node("n3", "N3", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        assert not any(i.code == "UNREACHABLE_NODE" for i in issues)

    def test_single_unreachable_node(self) -> None:
        """Test detection of single unreachable node."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")
        node3 = Node("n3", "N3", NodeType.MODULE, "m")  # Unreachable
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        unreachable_issues = [i for i in issues if i.code == "UNREACHABLE_NODE"]
        assert len(unreachable_issues) == 1
        assert any(i.severity == Severity.WARNING for i in unreachable_issues)
        assert any("n3" in i.message for i in unreachable_issues)
        assert any("agent.workflows[0].nodes[2]" in i.path for i in unreachable_issues)

    def test_multiple_unreachable_nodes(self) -> None:
        """Test detection of multiple unreachable nodes."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m")
        node2 = Node("n2", "N2", NodeType.MODULE, "m")  # Unreachable
        node3 = Node("n3", "N3", NodeType.MODULE, "m")  # Unreachable
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        unreachable_issues = [i for i in issues if i.code == "UNREACHABLE_NODE"]
        assert len(unreachable_issues) == 2
        assert any("n2" in i.message for i in unreachable_issues)
        assert any("n3" in i.message for i in unreachable_issues)

    def test_isolated_subgraph(self) -> None:
        """Test detection of isolated subgraph."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m")
        # n2 and n3 form isolated subgraph
        node2 = Node("n2", "N2", NodeType.MODULE, "m", next_nodes=("n3",))
        node3 = Node("n3", "N3", NodeType.MODULE, "m")
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        unreachable_issues = [i for i in issues if i.code == "UNREACHABLE_NODE"]
        assert len(unreachable_issues) == 2


class TestStaticAnalyzerUnusedResources:
    """Tests for unused resource detection."""

    def test_all_resources_used(self) -> None:
        """Test that all used resources pass check."""
        module = Module("m", "M")
        prompt = Prompt("p", "P", "Template")
        tool = Tool("t", "T")
        node1 = Node("n1", "N1", NodeType.MODULE, "m")
        node2 = Node("n2", "N2", NodeType.PROMPT, "p")
        node3 = Node("n3", "N3", NodeType.TOOL, "t")
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
            prompts=(prompt,),
            tools=(tool,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        assert not any(i.code == "UNUSED_MODULE" for i in issues)
        assert not any(i.code == "UNUSED_PROMPT" for i in issues)
        assert not any(i.code == "UNUSED_TOOL" for i in issues)

    def test_unused_module(self) -> None:
        """Test detection of unused module."""
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

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        unused_issues = [i for i in issues if i.code == "UNUSED_MODULE"]
        assert len(unused_issues) == 1
        assert any(i.severity == Severity.WARNING for i in unused_issues)
        assert any("m2" in i.message for i in unused_issues)
        assert any("agent.modules[1]" in i.path for i in unused_issues)

    def test_unused_prompt(self) -> None:
        """Test detection of unused prompt."""
        module = Module("m", "M")
        prompt1 = Prompt("p1", "P1", "Template1")
        prompt2 = Prompt("p2", "P2", "Template2")  # Unused
        node = Node("n", "N", NodeType.PROMPT, "p1")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
            prompts=(prompt1, prompt2),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        unused_issues = [i for i in issues if i.code == "UNUSED_PROMPT"]
        assert len(unused_issues) == 1
        assert any("p2" in i.message for i in unused_issues)
        assert any("agent.prompts[1]" in i.path for i in unused_issues)

    def test_unused_tool(self) -> None:
        """Test detection of unused tool."""
        module = Module("m", "M")
        tool1 = Tool("t1", "T1")
        tool2 = Tool("t2", "T2")  # Unused
        node = Node("n", "N", NodeType.TOOL, "t1")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
            tools=(tool1, tool2),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        unused_issues = [i for i in issues if i.code == "UNUSED_TOOL"]
        assert len(unused_issues) == 1
        assert any("t2" in i.message for i in unused_issues)
        assert any("agent.tools[1]" in i.path for i in unused_issues)

    def test_multiple_unused_resources(self) -> None:
        """Test detection of multiple unused resources."""
        module1 = Module("m1", "M1")
        module2 = Module("m2", "M2")  # Unused
        prompt1 = Prompt("p1", "P1", "T1")
        prompt2 = Prompt("p2", "P2", "T2")  # Unused
        tool1 = Tool("t1", "T1")
        tool2 = Tool("t2", "T2")  # Unused
        node = Node("n", "N", NodeType.MODULE, "m1")
        workflow = Workflow("main", "Main", (node,), "n")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module1, module2),
            prompts=(prompt1, prompt2),
            tools=(tool1, tool2),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        assert any(i.code == "UNUSED_MODULE" for i in issues)
        assert any(i.code == "UNUSED_PROMPT" for i in issues)
        assert any(i.code == "UNUSED_TOOL" for i in issues)


class TestStaticAnalyzerDeadEndNodes:
    """Tests for dead-end node detection."""

    def test_no_dead_ends(self) -> None:
        """Test that nodes with next_nodes or outputs pass check."""
        module = Module("m", "M")
        # Node with next_nodes
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        # Terminal node with outputs
        node2 = Node("n2", "N2", NodeType.MODULE, "m", outputs=("result",))
        workflow = Workflow("main", "Main", (node1, node2), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        assert not any(i.code == "POTENTIAL_DEAD_END" for i in issues)

    def test_dead_end_node(self) -> None:
        """Test detection of dead-end node (no next_nodes, no outputs)."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")  # Dead-end
        workflow = Workflow("main", "Main", (node1, node2), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        dead_end_issues = [i for i in issues if i.code == "POTENTIAL_DEAD_END"]
        assert len(dead_end_issues) == 1
        assert any(i.severity == Severity.WARNING for i in dead_end_issues)
        assert any("n2" in i.message for i in dead_end_issues)
        assert any("agent.workflows[0].nodes[1]" in i.path for i in dead_end_issues)

    def test_multiple_dead_ends(self) -> None:
        """Test detection of multiple dead-end nodes."""
        module = Module("m", "M")
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2", "n3"))
        node2 = Node("n2", "N2", NodeType.MODULE, "m")  # Dead-end
        node3 = Node("n3", "N3", NodeType.MODULE, "m")  # Dead-end
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        dead_end_issues = [i for i in issues if i.code == "POTENTIAL_DEAD_END"]
        assert len(dead_end_issues) == 2
        assert any("n2" in i.message for i in dead_end_issues)
        assert any("n3" in i.message for i in dead_end_issues)

    def test_terminal_node_with_outputs(self) -> None:
        """Test that terminal nodes with outputs are not flagged."""
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

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        assert not any(i.code == "POTENTIAL_DEAD_END" for i in issues)


class TestStaticAnalyzerMultipleIssues:
    """Tests for detecting multiple issues in one analysis."""

    def test_multiple_issue_types(self) -> None:
        """Test that multiple types of issues are detected in one pass."""
        module1 = Module("m1", "M1")
        module2 = Module("m2", "M2")  # Unused
        # Circular dependency: n1 -> n2 -> n1
        node1 = Node("n1", "N1", NodeType.MODULE, "m1", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m1", next_nodes=("n1",))
        node3 = Node("n3", "N3", NodeType.MODULE, "m1")  # Unreachable + Dead-end
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module1, module2),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        # Should detect all issue types
        assert any(i.code == "CIRCULAR_DEPENDENCY" for i in issues)
        assert any(i.code == "UNREACHABLE_NODE" for i in issues)
        assert any(i.code == "UNUSED_MODULE" for i in issues)
        assert any(i.code == "POTENTIAL_DEAD_END" for i in issues)

    def test_multiple_workflows(self) -> None:
        """Test analysis across multiple workflows."""
        module = Module("m", "M")
        # Workflow 1: circular dependency
        node1 = Node("n1", "N1", NodeType.MODULE, "m", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m", next_nodes=("n1",))
        workflow1 = Workflow("wf1", "WF1", (node1, node2), "n1")

        # Workflow 2: unreachable node
        node3 = Node("n3", "N3", NodeType.MODULE, "m")
        node4 = Node("n4", "N4", NodeType.MODULE, "m")  # Unreachable
        workflow2 = Workflow("wf2", "WF2", (node3, node4), "n3")

        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow1, workflow2),
            modules=(module,),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        # Should detect issues in both workflows
        assert any(i.code == "CIRCULAR_DEPENDENCY" for i in issues)
        assert any(i.code == "UNREACHABLE_NODE" for i in issues)
        assert any("agent.workflows[0]" in i.path for i in issues)
        assert any("agent.workflows[1]" in i.path for i in issues)

    def test_severity_levels(self) -> None:
        """Test that different issues have appropriate severity levels."""
        module1 = Module("m1", "M1")
        module2 = Module("m2", "M2")  # Unused
        node1 = Node("n1", "N1", NodeType.MODULE, "m1", next_nodes=("n2",))
        node2 = Node("n2", "N2", NodeType.MODULE, "m1", next_nodes=("n1",))  # Circular
        node3 = Node("n3", "N3", NodeType.MODULE, "m1")  # Unreachable
        workflow = Workflow("main", "Main", (node1, node2, node3), "n1")
        agent = AgentDefinition(
            name="test",
            version="1.0.0",
            description="Test",
            workflows=(workflow,),
            modules=(module1, module2),
        )

        analyzer = StaticAnalyzer()
        issues = analyzer.analyze(agent)

        # Circular dependencies should be ERROR
        circular = [i for i in issues if i.code == "CIRCULAR_DEPENDENCY"]
        assert all(i.severity == Severity.ERROR for i in circular)

        # Unreachable nodes should be WARNING
        unreachable = [i for i in issues if i.code == "UNREACHABLE_NODE"]
        assert all(i.severity == Severity.WARNING for i in unreachable)

        # Unused resources should be WARNING
        unused = [i for i in issues if i.code == "UNUSED_MODULE"]
        assert all(i.severity == Severity.WARNING for i in unused)
