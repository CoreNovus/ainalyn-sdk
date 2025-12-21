# Ainalyn SDK

Build task-oriented agents with Python. The Ainalyn SDK is a compiler that turns your Python code into platform-ready agent definitions.

!!! note "SDK = Compiler, Not Runtime"
    The SDK creates agent descriptions. The Ainalyn Platform executes them.

## What it does

- **Define** agents with a Python API
- **Validate** definitions before deployment
- **Export** to YAML for the platform

## Features

- **Type-safe API** - Full type hints and IDE autocomplete
- **Fluent builders** - Chainable, intuitive API
- **Validation** - Catch errors before deployment
- **YAML export** - One command to platform-ready format

## Example

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate, export_yaml

# Define an agent
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

# Validate and export
validate(agent)
yaml_output = export_yaml(agent)
```

## Getting Started

**New to the SDK?**

1. [Install](getting-started/installation.md) the SDK
2. Try the [5-minute quickstart](getting-started/quickstart.md)
3. Build [your first agent](getting-started/your-first-agent.md)

**Understanding the SDK**

- [Platform Boundaries](concepts/platform-boundaries.md) - What the SDK can and cannot do
- [Compiler vs Runtime](concepts/compiler-not-runtime.md) - Why the SDK is a compiler
- [Architecture](concepts/architecture-overview.md) - How it's built
- [Agent Definitions](concepts/agent-definition.md) - What you're creating

## Important: SDK Boundaries

**The SDK creates descriptions. The platform runs them.**

What the SDK does:
- ✅ Define agent structures
- ✅ Validate definitions
- ✅ Export to YAML

What the SDK does NOT do:
- ❌ Execute agents
- ❌ Handle billing
- ❌ Manage retries or timeouts

[Learn more about platform boundaries →](concepts/platform-boundaries.md)

## Support

- [Report issues](https://github.com/CoreNovus/ainalyn-sdk/issues)
- [Ask questions](https://github.com/CoreNovus/ainalyn-sdk/discussions)
- [View source](https://github.com/CoreNovus/ainalyn-sdk)
