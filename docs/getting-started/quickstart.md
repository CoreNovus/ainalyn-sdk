# Quickstart

Build your first agent in 5 minutes.

## Install

```bash
pip install ainalyn-sdk
```

## Create an Agent

Create `my_agent.py`:

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate, export_yaml

# Define the agent
agent = (
    AgentBuilder("GreetingAgent")
    .description("Generates personalized greetings")
    .version("1.0.0")
    .add_workflow(
        WorkflowBuilder("greet_user")
        .add_node(
            NodeBuilder("generate_greeting")
            .goal("Generate a personalized greeting")
            .build()
        )
        .build()
    )
    .build()
)

# Validate
validate(agent)
print("✅ Valid!")

# Export to YAML
yaml_output = export_yaml(agent)
print(yaml_output)
```

## Run

```bash
python my_agent.py
```

Output:
```
✅ Valid!
name: GreetingAgent
version: 1.0.0
description: Generates personalized greetings
workflows:
  - name: greet_user
    nodes:
      - name: generate_greeting
        goal: Generate a personalized greeting
```

## What's Happening

1. **AgentBuilder** creates an agent
2. **WorkflowBuilder** adds a workflow
3. **NodeBuilder** adds a task node
4. **validate()** checks the definition
5. **export_yaml()** converts to YAML

## Next Steps

- [Build a more complex agent](your-first-agent.md)
- [Understand platform boundaries](../concepts/platform-boundaries.md)
- [Explore the API](../api-reference/api.md)

## Using the CLI

You can also use the command line:

```bash
# Validate
ainalyn validate my_agent.py

# Compile to YAML
ainalyn compile my_agent.py -o output.yaml
```

## Common Patterns

**Multiple nodes with dependencies:**
```python
workflow = (
    WorkflowBuilder("process")
    .add_node(
        NodeBuilder("step1")
        .goal("First step")
        .build()
    )
    .add_node(
        NodeBuilder("step2")
        .goal("Second step")
        .depends_on("step1")
        .build()
    )
    .build()
)
```

**Multiple workflows:**
```python
agent = (
    AgentBuilder("MyAgent")
    .version("1.0.0")
    .add_workflow(workflow1)
    .add_workflow(workflow2)
    .build()
)
```

## Need Help?

- [Full tutorial](your-first-agent.md)
- [API reference](../api-reference/builders.md)
- [Report issues](https://github.com/CoreNovus/ainalyn-sdk/issues)
