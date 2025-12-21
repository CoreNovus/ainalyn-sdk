# Quickstart Guide

Get up and running with the Ainalyn SDK in under 5 minutes! This guide will walk you through creating, validating, and exporting your first agent definition.

## Prerequisites

Ensure you have the Ainalyn SDK installed:

```bash
pip install ainalyn-sdk
```

See [Installation](installation.md) for detailed setup instructions.

## 5-Minute Tutorial

### Step 1: Create a Simple Agent (2 minutes)

Create a new Python file called `my_first_agent.py`:

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder

# Build a simple greeting agent
agent = (
    AgentBuilder("GreetingAgent")
    .description("A friendly agent that generates personalized greetings")
    .version("1.0.0")
    .add_workflow(
        WorkflowBuilder("greet_user")
        .add_node(
            NodeBuilder("generate_greeting")
            .goal("Generate a personalized greeting message")
            .build()
        )
        .build()
    )
    .build()
)

print(f"✅ Created agent: {agent.name} v{agent.version}")
```

Run it:

```bash
python my_first_agent.py
```

Output:
```
✅ Created agent: GreetingAgent v1.0.0
```

### Step 2: Validate the Agent (1 minute)

Add validation to ensure your agent complies with platform rules:

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate

agent = (
    AgentBuilder("GreetingAgent")
    .description("A friendly agent that generates personalized greetings")
    .version("1.0.0")
    .add_workflow(
        WorkflowBuilder("greet_user")
        .add_node(
            NodeBuilder("generate_greeting")
            .goal("Generate a personalized greeting message")
            .build()
        )
        .build()
    )
    .build()
)

# Validate the agent definition
try:
    validate(agent)
    print("✅ Agent definition is valid!")
except Exception as e:
    print(f"❌ Validation failed: {e}")
```

Run it:

```bash
python my_first_agent.py
```

Output:
```
✅ Agent definition is valid!
```

### Step 3: Export to YAML (2 minutes)

Export your agent definition to YAML format for platform deployment:

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate, export_yaml

agent = (
    AgentBuilder("GreetingAgent")
    .description("A friendly agent that generates personalized greetings")
    .version("1.0.0")
    .add_workflow(
        WorkflowBuilder("greet_user")
        .add_node(
            NodeBuilder("generate_greeting")
            .goal("Generate a personalized greeting message")
            .build()
        )
        .build()
    )
    .build()
)

# Validate and export
validate(agent)
yaml_output = export_yaml(agent)

# Save to file
with open("greeting_agent.yaml", "w") as f:
    f.write(yaml_output)

print("✅ Agent exported to greeting_agent.yaml")
print("\n--- YAML Output ---")
print(yaml_output)
```

Run it:

```bash
python my_first_agent.py
```

Output:
```
✅ Agent exported to greeting_agent.yaml

--- YAML Output ---
name: GreetingAgent
version: 1.0.0
description: A friendly agent that generates personalized greetings
workflows:
  - name: greet_user
    nodes:
      - name: generate_greeting
        goal: Generate a personalized greeting message
        dependencies: []
```

## What You Just Did

Congratulations! You've successfully:

1. ✅ **Built** an agent definition using the Builder API
2. ✅ **Validated** the definition against platform rules
3. ✅ **Exported** the definition to deployment-ready YAML

## Using the CLI

You can also work with agent definitions using the command-line interface:

### Validate an Agent Definition

Create a Python file that defines your agent:

```python
# agent_def.py
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder

agent = (
    AgentBuilder("MyAgent")
    .description("My custom agent")
    .version("1.0.0")
    .add_workflow(
        WorkflowBuilder("main_workflow")
        .add_node(
            NodeBuilder("task_1")
            .goal("Complete task 1")
            .build()
        )
        .build()
    )
    .build()
)
```

Validate it using the CLI:

```bash
ainalyn validate agent_def.py
```

### Compile to YAML

Compile the agent definition to YAML:

```bash
ainalyn compile agent_def.py --output my_agent.yaml
```

## Next Steps

Now that you've created your first agent, explore these topics:

### Learn Core Concepts

- **[Platform Boundaries](../concepts/platform-boundaries.md)** - Understand what the SDK can and cannot do
- **[Compiler vs Runtime](../concepts/compiler-not-runtime.md)** - Why the SDK is a compiler, not an execution engine
- **[Agent Definition](../concepts/agent-definition.md)** - Deep dive into agent structure

### Build More Complex Agents

- **[Your First Agent (Detailed)](your-first-agent.md)** - Step-by-step tutorial with explanations
- **[Using Builder API](../user-guide/building-agents/using-builder-api.md)** - Complete builder API guide
- **[Defining Workflows](../user-guide/building-agents/defining-workflows.md)** - Advanced workflow patterns

### Explore Examples

- **[Basic Agent](../examples/basic-agent.md)** - Simple agent example
- **[Multi-Workflow Agent](../examples/multi-workflow-agent.md)** - Complex workflows
- **[Reusable Modules](../examples/reusable-modules.md)** - Module patterns

### Check the API Reference

- **[AgentBuilder](../api-reference/builders/agent-builder.md)** - Complete AgentBuilder API
- **[WorkflowBuilder](../api-reference/builders/workflow-builder.md)** - Complete WorkflowBuilder API
- **[NodeBuilder](../api-reference/builders/node-builder.md)** - Complete NodeBuilder API

## Common Patterns

### Adding Multiple Workflows

```python
agent = (
    AgentBuilder("MultiWorkflowAgent")
    .description("Agent with multiple workflows")
    .version("1.0.0")
    .add_workflow(
        WorkflowBuilder("workflow_1")
        .add_node(NodeBuilder("task_1").goal("Do task 1").build())
        .build()
    )
    .add_workflow(
        WorkflowBuilder("workflow_2")
        .add_node(NodeBuilder("task_2").goal("Do task 2").build())
        .build()
    )
    .build()
)
```

### Adding Node Dependencies

```python
workflow = (
    WorkflowBuilder("sequential_workflow")
    .add_node(
        NodeBuilder("step_1")
        .goal("Complete step 1")
        .build()
    )
    .add_node(
        NodeBuilder("step_2")
        .goal("Complete step 2")
        .depends_on("step_1")  # step_2 depends on step_1
        .build()
    )
    .add_node(
        NodeBuilder("step_3")
        .goal("Complete step 3")
        .depends_on("step_1", "step_2")  # step_3 depends on both
        .build()
    )
    .build()
)
```

### Adding Modules for Reusability

```python
from ainalyn import ModuleBuilder

module = (
    ModuleBuilder("DataProcessor")
    .description("Reusable data processing module")
    .add_capability("parse_csv")
    .add_capability("validate_data")
    .build()
)

agent = (
    AgentBuilder("DataAgent")
    .version("1.0.0")
    .add_module(module)
    .add_workflow(...)
    .build()
)
```

## Quick Reference

### Key Imports

```python
# Builders
from ainalyn import (
    AgentBuilder,
    WorkflowBuilder,
    NodeBuilder,
    ModuleBuilder,
    PromptBuilder,
    ToolBuilder,
)

# API Functions
from ainalyn.api import validate, export_yaml, compile_agent

# Entities (usually not imported directly)
from ainalyn.domain.entities import (
    AgentDefinition,
    Workflow,
    Node,
    Module,
    Prompt,
    Tool,
)
```

### Builder Pattern Cheat Sheet

```python
# All builders follow this pattern:
builder = (
    Builder("name")
    .method_1(...)
    .method_2(...)
    .build()  # Always call .build() at the end!
)
```

### Validation and Export

```python
# Validate
from ainalyn.api import validate
validate(agent)  # Raises exception if invalid

# Export to YAML
from ainalyn.api import export_yaml
yaml_str = export_yaml(agent)

# Compile (validate + export)
from ainalyn.api import compile_agent
yaml_str = compile_agent(agent)  # Validates first, then exports
```

## Troubleshooting

### Common Errors

**Error: `Builder().build() not called`**

❌ **Wrong:**
```python
workflow = WorkflowBuilder("my_workflow")  # Missing .build()
```

✅ **Correct:**
```python
workflow = WorkflowBuilder("my_workflow").build()
```

**Error: `Circular dependency detected`**

This happens when nodes depend on each other in a circular way:

❌ **Wrong:**
```python
workflow = (
    WorkflowBuilder("circular")
    .add_node(NodeBuilder("A").depends_on("B").build())
    .add_node(NodeBuilder("B").depends_on("A").build())  # Circular!
    .build()
)
```

**Error: `Validation failed: Invalid name format`**

Names must be valid Python identifiers:

❌ **Wrong:**
```python
AgentBuilder("my-agent")  # Hyphens not allowed
AgentBuilder("my agent")  # Spaces not allowed
AgentBuilder("123agent")  # Cannot start with number
```

✅ **Correct:**
```python
AgentBuilder("my_agent")  # Underscores OK
AgentBuilder("MyAgent")   # CamelCase OK
AgentBuilder("agent123")  # Numbers OK (not at start)
```

## Getting Help

- **Questions?** Check the [Troubleshooting Guide](../troubleshooting.md)
- **Found a bug?** [Report it on GitHub](https://github.com/ainalyn/ainalyn-sdk/issues)
- **Need support?** Email dev@ainalyn.io

---

**What's next?** Continue to [Your First Agent](your-first-agent.md) for a detailed, explained walkthrough!
