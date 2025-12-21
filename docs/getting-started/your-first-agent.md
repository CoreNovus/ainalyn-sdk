# Your First Agent: Detailed Tutorial

This comprehensive tutorial will guide you through building a complete, real-world agent step by step. By the end, you'll understand the Builder API, validation rules, and export process.

## What We'll Build

We'll create a **Research Assistant Agent** that:

- Searches for information on a given topic
- Analyzes and summarizes the findings
- Generates a structured report

This agent will have a single workflow with three sequential nodes.

## Prerequisites

- Ainalyn SDK installed ([Installation Guide](installation.md))
- Basic Python knowledge
- A text editor or IDE

## Step-by-Step Implementation

### Step 1: Project Setup

Create a new project directory and file:

```bash
mkdir research-agent
cd research-agent
touch research_agent.py
```

### Step 2: Import Required Components

Open `research_agent.py` and start with imports:

```python
"""Research Assistant Agent - A complete example."""
from __future__ import annotations

from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate, export_yaml
```

**What's happening:**

- `AgentBuilder`: Used to construct the agent definition
- `WorkflowBuilder`: Used to define workflows
- `NodeBuilder`: Used to create individual task nodes
- `validate`: Validates the agent against platform rules
- `export_yaml`: Exports the agent to YAML format

### Step 3: Build the First Node

Let's create the first node that searches for information:

```python
# Node 1: Search for information
search_node = (
    NodeBuilder("search_information")
    .goal("Search and collect relevant information on the given topic")
    .description(
        "This node performs web searches or retrieves information from "
        "available knowledge sources about the user's specified topic."
    )
    .build()
)
```

**Key points:**

- **Name**: `"search_information"` - must be a valid Python identifier
- **Goal**: A clear, concise statement of what this node should accomplish
- **Description** (optional): Additional context about the node's purpose
- **`.build()`**: Always call this to finalize the node

### Step 4: Build the Second Node

Create the analysis node that depends on the search node:

```python
# Node 2: Analyze findings (depends on Node 1)
analyze_node = (
    NodeBuilder("analyze_findings")
    .goal("Analyze the collected information and identify key insights")
    .description(
        "This node processes the search results, extracts key points, "
        "and identifies patterns or important findings."
    )
    .depends_on("search_information")  # Explicit dependency
    .build()
)
```

**New concept: Dependencies**

- `.depends_on("search_information")` means this node won't run until `search_information` completes
- Dependencies create a directed acyclic graph (DAG) of execution
- You can depend on multiple nodes: `.depends_on("node1", "node2")`

### Step 5: Build the Third Node

Create the report generation node:

```python
# Node 3: Generate report (depends on Node 2)
report_node = (
    NodeBuilder("generate_report")
    .goal("Create a structured research report from the analysis")
    .description(
        "This node formats the analyzed information into a well-structured "
        "report with introduction, findings, and conclusions."
    )
    .depends_on("analyze_findings")  # Depends on analysis
    .build()
)
```

**Execution order:**

With these dependencies, the execution order is:
1. `search_information` (no dependencies, runs first)
2. `analyze_findings` (depends on search, runs second)
3. `generate_report` (depends on analysis, runs third)

### Step 6: Build the Workflow

Now combine the nodes into a workflow:

```python
# Create the workflow with all three nodes
research_workflow = (
    WorkflowBuilder("conduct_research")
    .description("Workflow for conducting research and generating reports")
    .add_node(search_node)
    .add_node(analyze_node)
    .add_node(report_node)
    .build()
)
```

**Key points:**

- Workflows are named collections of nodes
- Nodes are added in any order (dependencies determine execution order)
- Always call `.build()` when done

### Step 7: Build the Agent

Finally, create the complete agent definition:

```python
# Create the complete agent
research_agent = (
    AgentBuilder("ResearchAssistant")
    .description(
        "An intelligent research assistant that searches for information, "
        "analyzes findings, and generates comprehensive research reports."
    )
    .version("1.0.0")
    .add_workflow(research_workflow)
    .build()
)
```

**Agent properties:**

- **Name**: `"ResearchAssistant"` - unique identifier
- **Description**: What the agent does (shown in marketplace)
- **Version**: Semantic versioning (e.g., "1.0.0", "2.1.3")
- **Workflows**: One or more workflows the agent can execute

### Step 8: Validate the Agent

Add validation to ensure compliance:

```python
# Validate the agent definition
try:
    validate(research_agent)
    print("✅ Agent validation successful!")
except Exception as e:
    print(f"❌ Validation failed: {e}")
    exit(1)
```

**What validation checks:**

- ✅ Names are valid Python identifiers
- ✅ Required fields are present
- ✅ No circular dependencies in workflows
- ✅ Platform boundary compliance (no forbidden patterns)
- ✅ Semantic versioning format

### Step 9: Export to YAML

Export the validated agent to YAML:

```python
# Export to YAML
yaml_output = export_yaml(research_agent)

# Print to console
print("\n--- Generated YAML ---")
print(yaml_output)

# Save to file
output_file = "research_assistant.yaml"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(yaml_output)

print(f"\n✅ Agent exported to {output_file}")
```

### Step 10: Add a Main Block

Add a standard Python main block:

```python
if __name__ == "__main__":
    print("Building Research Assistant Agent...")
    print(f"Agent: {research_agent.name} v{research_agent.version}")
    print(f"Workflows: {len(research_agent.workflows)}")
    print(f"Total nodes: {sum(len(w.nodes) for w in research_agent.workflows)}")
```

## Complete Code

Here's the full `research_agent.py`:

```python
"""Research Assistant Agent - A complete example."""
from __future__ import annotations

from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate, export_yaml


# Node 1: Search for information
search_node = (
    NodeBuilder("search_information")
    .goal("Search and collect relevant information on the given topic")
    .description(
        "This node performs web searches or retrieves information from "
        "available knowledge sources about the user's specified topic."
    )
    .build()
)

# Node 2: Analyze findings (depends on Node 1)
analyze_node = (
    NodeBuilder("analyze_findings")
    .goal("Analyze the collected information and identify key insights")
    .description(
        "This node processes the search results, extracts key points, "
        "and identifies patterns or important findings."
    )
    .depends_on("search_information")
    .build()
)

# Node 3: Generate report (depends on Node 2)
report_node = (
    NodeBuilder("generate_report")
    .goal("Create a structured research report from the analysis")
    .description(
        "This node formats the analyzed information into a well-structured "
        "report with introduction, findings, and conclusions."
    )
    .depends_on("analyze_findings")
    .build()
)

# Create the workflow with all three nodes
research_workflow = (
    WorkflowBuilder("conduct_research")
    .description("Workflow for conducting research and generating reports")
    .add_node(search_node)
    .add_node(analyze_node)
    .add_node(report_node)
    .build()
)

# Create the complete agent
research_agent = (
    AgentBuilder("ResearchAssistant")
    .description(
        "An intelligent research assistant that searches for information, "
        "analyzes findings, and generates comprehensive research reports."
    )
    .version("1.0.0")
    .add_workflow(research_workflow)
    .build()
)

# Validate the agent definition
try:
    validate(research_agent)
    print("✅ Agent validation successful!")
except Exception as e:
    print(f"❌ Validation failed: {e}")
    exit(1)

# Export to YAML
yaml_output = export_yaml(research_agent)

# Print to console
print("\n--- Generated YAML ---")
print(yaml_output)

# Save to file
output_file = "research_assistant.yaml"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(yaml_output)

print(f"\n✅ Agent exported to {output_file}")

if __name__ == "__main__":
    print("Building Research Assistant Agent...")
    print(f"Agent: {research_agent.name} v{research_agent.version}")
    print(f"Workflows: {len(research_agent.workflows)}")
    print(f"Total nodes: {sum(len(w.nodes) for w in research_agent.workflows)}")
```

## Running the Agent

Execute the script:

```bash
python research_agent.py
```

Expected output:

```
Building Research Assistant Agent...
Agent: ResearchAssistant v1.0.0
Workflows: 1
Total nodes: 3
✅ Agent validation successful!

--- Generated YAML ---
name: ResearchAssistant
version: 1.0.0
description: An intelligent research assistant that searches for information, analyzes findings, and generates comprehensive research reports.
workflows:
  - name: conduct_research
    description: Workflow for conducting research and generating reports
    nodes:
      - name: search_information
        goal: Search and collect relevant information on the given topic
        description: This node performs web searches or retrieves information from available knowledge sources about the user's specified topic.
        dependencies: []
      - name: analyze_findings
        goal: Analyze the collected information and identify key insights
        description: This node processes the search results, extracts key points, and identifies patterns or important findings.
        dependencies:
          - search_information
      - name: generate_report
        goal: Create a structured research report from the analysis
        description: This node formats the analyzed information into a well-structured report with introduction, findings, and conclusions.
        dependencies:
          - analyze_findings

✅ Agent exported to research_assistant.yaml
```

## Understanding the Output

The generated YAML has this structure:

```yaml
name: ResearchAssistant          # Agent identifier
version: 1.0.0                   # Semantic version
description: ...                 # What the agent does

workflows:                       # List of workflows
  - name: conduct_research       # Workflow identifier
    description: ...             # Workflow purpose
    nodes:                       # List of nodes in workflow
      - name: search_information # Node identifier
        goal: ...                # Node objective
        description: ...         # Node details
        dependencies: []         # No dependencies for first node

      - name: analyze_findings
        goal: ...
        description: ...
        dependencies:
          - search_information   # Depends on first node

      - name: generate_report
        goal: ...
        description: ...
        dependencies:
          - analyze_findings     # Depends on second node
```

This YAML is ready for deployment to the Ainalyn Platform!

## Key Takeaways

### 1. The Builder Pattern

All construction uses the builder pattern:

```python
result = (
    Builder("name")
    .method_1(arg1)
    .method_2(arg2)
    .build()  # Always end with .build()!
)
```

### 2. Building Bottom-Up

Build from the smallest components to largest:

1. **Nodes** (smallest units of work)
2. **Workflows** (collections of nodes)
3. **Agent** (collection of workflows, modules, prompts, tools)

### 3. Dependencies Create Order

- Use `.depends_on("node_name")` to create execution order
- Dependencies must not create cycles
- The platform determines actual execution, not the SDK

### 4. Always Validate

```python
validate(agent)  # Catches errors early!
```

### 5. SDK = Compiler, Not Runtime

Remember: The SDK **describes** agents, it does not **execute** them. The YAML you export is consumed by the Ainalyn Platform for actual execution.

## Next Steps

### Enhance Your Agent

Try adding these features to your research agent:

1. **Add a second workflow** for quick fact-checking
2. **Add modules** for reusable capabilities
3. **Add prompts** to guide LLM behavior
4. **Add tools** to specify external integrations

### Explore Advanced Topics

- **[Defining Workflows](../user-guide/building-agents/defining-workflows.md)** - Advanced workflow patterns
- **[Creating Nodes](../user-guide/building-agents/creating-nodes.md)** - Node configuration options
- **[Adding Modules](../user-guide/building-agents/adding-modules.md)** - Reusable components

### Study Examples

- **[Multi-Workflow Agent](../examples/multi-workflow-agent.md)** - Agents with multiple workflows
- **[Reusable Modules](../examples/reusable-modules.md)** - Module patterns

### Learn Core Concepts

- **[Platform Boundaries](../concepts/platform-boundaries.md)** - What the SDK cannot do
- **[Compiler vs Runtime](../concepts/compiler-not-runtime.md)** - Why the distinction matters

## Common Mistakes

### Forgetting `.build()`

❌ **Wrong:**
```python
node = NodeBuilder("my_node").goal("Do something")
# Missing .build()!
```

✅ **Correct:**
```python
node = NodeBuilder("my_node").goal("Do something").build()
```

### Circular Dependencies

❌ **Wrong:**
```python
workflow = (
    WorkflowBuilder("circular")
    .add_node(NodeBuilder("A").depends_on("B").build())
    .add_node(NodeBuilder("B").depends_on("A").build())  # A→B→A = circular!
    .build()
)
```

✅ **Correct:**
```python
workflow = (
    WorkflowBuilder("sequential")
    .add_node(NodeBuilder("A").build())  # No dependencies
    .add_node(NodeBuilder("B").depends_on("A").build())  # A→B (acyclic)
    .build()
)
```

### Invalid Names

❌ **Wrong:**
```python
AgentBuilder("my-agent")   # Hyphens not allowed
AgentBuilder("my agent")   # Spaces not allowed
AgentBuilder("123agent")   # Cannot start with digit
```

✅ **Correct:**
```python
AgentBuilder("my_agent")   # Underscores OK
AgentBuilder("MyAgent")    # CamelCase OK
AgentBuilder("agent123")   # Digits OK (not at start)
```

## Getting Help

- **Questions?** Check the [Troubleshooting Guide](../troubleshooting.md)
- **API details?** See [API Reference](../api-reference/builders/agent-builder.md)
- **Found a bug?** [Report it](https://github.com/ainalyn/ainalyn-sdk/issues)
- **Need support?** Email dev@ainalyn.io

---

**Congratulations!** You've built your first complete agent. Keep exploring to master the Ainalyn SDK!
