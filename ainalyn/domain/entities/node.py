from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class NodeType(Enum):
    """
    The type of resource that a Node references.

    This enum defines the possible types of resources that can be
    referenced by a Node within a Workflow.

    Attributes:
        MODULE: References a Module (reusable capability unit)
        PROMPT: References a Prompt (LLM prompt template)
        TOOL: References a Tool (external tool interface)
    """

    MODULE = "module"
    PROMPT = "prompt"
    TOOL = "tool"


@dataclass(frozen=True, slots=True)
class Node:
    """
    A processing step within a Workflow.

    Node represents a single unit of work in a Workflow. Each Node
    references exactly one Module, Prompt, or Tool to perform its
    designated task. Nodes can be connected to form a directed graph
    that describes the task flow.

    This is a pure description entity with no execution semantics.
    The actual execution is handled by Platform Core.

    Attributes:
        name: Unique identifier for this Node within its Workflow.
            Must match pattern [a-z0-9-]+.
        description: Human-readable description of what this Node does.
        node_type: The type of resource this Node references
            (MODULE, PROMPT, or TOOL).
        reference: The name of the referenced module/prompt/tool.
            Must exist in the AgentDefinition.
        inputs: Names of input parameters this Node expects.
            These are mapped from outputs of previous Nodes.
        outputs: Names of output parameters this Node produces.
            These can be consumed by subsequent Nodes.
        next_nodes: Names of Nodes that follow this one in the flow.
            Empty tuple indicates this is a terminal Node.

    Example:
        >>> node = Node(
        ...     name="fetch-data",
        ...     description="Fetches data from external API",
        ...     node_type=NodeType.MODULE,
        ...     reference="http-fetcher",
        ...     outputs=("raw_data",),
        ...     next_nodes=("process-data",),
        ... )
    """

    name: str
    description: str
    node_type: NodeType
    reference: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    next_nodes: tuple[str, ...] = ()
