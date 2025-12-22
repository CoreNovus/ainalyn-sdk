from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ainalyn.domain.entities.node import Node


@dataclass(frozen=True, slots=True)
class Workflow:
    """
    A structural description of a task flow.

    Workflow defines a complete task flow composed of multiple
    Nodes. It describes the sequence and data flow between processing
    steps, forming a directed graph of operations.

    This is a pure description entity. The actual execution orchestration
    is handled by Platform Core.

    Attributes:
        name: Unique identifier for this Workflow within the AgentDefinition.
            Must match pattern [a-z0-9-]+.
        description: Human-readable description of what this Workflow
            accomplishes.
        nodes: Tuple of Nodes that comprise this Workflow. Each Node
            represents a processing step in the flow.
        entry_node: Name of the starting Node in this flow. This Node
            must exist in the nodes tuple.

    Example:
        >>> from ainalyn.domain.entities.node import Node, NodeType
        >>> workflow = Workflow(
        ...     name="data-processing-pipeline",
        ...     description="Fetches, processes, and stores data",
        ...     entry_node="fetch",
        ...     nodes=(
        ...         Node(
        ...             name="fetch",
        ...             description="Fetch raw data",
        ...             node_type=NodeType.MODULE,
        ...             reference="http-fetcher",
        ...             outputs=("raw_data",),
        ...             next_nodes=("process",),
        ...         ),
        ...         Node(
        ...             name="process",
        ...             description="Process the data",
        ...             node_type=NodeType.PROMPT,
        ...             reference="data-processor",
        ...             inputs=("raw_data",),
        ...             outputs=("processed_data",),
        ...             next_nodes=("store",),
        ...         ),
        ...         Node(
        ...             name="store",
        ...             description="Store the results",
        ...             node_type=NodeType.TOOL,
        ...             reference="file-writer",
        ...             inputs=("processed_data",),
        ...         ),
        ...     ),
        ... )
    """

    name: str
    description: str
    nodes: tuple[Node, ...]
    entry_node: str
