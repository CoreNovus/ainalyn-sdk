# Ainalyn SDK

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/ainalyn-sdk)](https://pypi.org/project/ainalyn-sdk/)
[![Tests](https://img.shields.io/badge/tests-175%20passed-success)](https://github.com/CoreNovus/ainalyn-sdk)

> **Official Python SDK for building task-oriented agents on Ainalyn Platform**

Build, validate, and deploy AI agents with type-safe Python builders and automatic runtime handling.

---

## 🚀 Quick Start

### Installation

```bash
pip install ainalyn-sdk
```

### Your First Agent (30 seconds)

```python
from ainalyn import AgentBuilder, ModuleBuilder, WorkflowBuilder, NodeBuilder

# Define your agent
agent = (
    AgentBuilder("my-agent")
    .version("1.0.0")
    .description("My first task-oriented agent")
    .add_module(
        ModuleBuilder("greeter")
        .description("Greets users")
        .input_schema({"type": "object", "properties": {"name": {"type": "string"}}})
        .output_schema({"type": "object", "properties": {"greeting": {"type": "string"}}})
        .build()
    )
    .add_workflow(
        WorkflowBuilder("main")
        .description("Main workflow")
        .add_node(
            NodeBuilder("greet")
            .description("Greet user")
            .uses_module("greeter")
            .build()
        )
        .entry_node("greet")
        .build()
    )
    .build()
)

# Compile to YAML
from ainalyn import compile_agent
yaml_output = compile_agent(agent)
print(yaml_output)
```

---

## 💡 What is Ainalyn SDK?

Ainalyn SDK enables developers to create **task-oriented agents** with two approaches:

### 📊 COMPOSITE Agents (Graph-First)
- Build workflows using **node-based graphs**
- Pure configuration - **no code required**
- Platform executes your workflow
- Perfect for: Data pipelines, orchestration, multi-step processes

### 💻 ATOMIC Agents (Code-First)
- Write **Python functions** with custom logic
- Full implementation control
- Deploy as **AWS Lambda** functions
- Perfect for: Custom algorithms, API integrations, data transformations

---

## 🎯 Key Features

✅ **Type-Safe Builders** - Full IDE autocomplete and compile-time validation
✅ **Comprehensive Validation** - Schema, static analysis, platform compliance checks
✅ **Runtime Wrapper** - SYNC/ASYNC execution modes with automatic routing
✅ **CLI Tools** - Validate and compile from command line
✅ **Production Ready** - 175 tests, >85% coverage, strict type checking

---

## 📖 Core Concepts

### Agent Definition Structure

```text
AgentDefinition
├── Metadata (name, version, description)
├── Modules (reusable components)
├── Prompts (LLM prompt templates)
├── Tools (external integrations)
└── Workflows (execution graphs)
    └── Nodes (workflow steps)
```

### Execution Modes

- **SYNC Mode**: Fast tasks (<29s) - immediate response
- **ASYNC Mode**: Long tasks (>29s) - polling-based with state management

### Platform Review Gates

The SDK validates against 5 platform compliance gates:
1. **Contract Completeness** - All schemas defined
2. **No Shadow Runtime** - Clear ATOMIC vs COMPOSITE distinction
3. **No Billing Authority** - Pricing is hint-only
4. **EIP Dependencies** - Valid dependency declarations

---

## 🛠️ Development Paths

### Path 1: COMPOSITE Agent (Graph-First)

```python
from ainalyn import AgentBuilder, ModuleBuilder, WorkflowBuilder, NodeBuilder

agent = (
    AgentBuilder("data-pipeline")
    .version("1.0.0")
    .description("Multi-step data processing pipeline")
    .add_module(...)  # Define reusable modules
    .add_workflow(
        WorkflowBuilder("main")
        .add_node(NodeBuilder("fetch").uses_module("http-fetcher").build())
        .add_node(NodeBuilder("process").uses_module("data-processor").build())
        .add_node(NodeBuilder("save").uses_module("data-saver").build())
        .entry_node("fetch")
        .build()
    )
    .build()
)

# Compile and submit to platform
from ainalyn import compile_agent
yaml_output = compile_agent(agent)
```

### Path 2: ATOMIC Agent (Code-First)

```python
from ainalyn.runtime import agent, ExecutionContext

@agent.atomic
def my_handler(context: ExecutionContext) -> dict:
    """Your custom business logic here"""
    user_input = context.input_data

    # Your implementation
    result = process_data(user_input)

    return {"output": result}

# Define agent metadata separately
from ainalyn import AgentBuilder
definition = (
    AgentBuilder("my-atomic-agent")
    .version("1.0.0")
    .description("Custom Python agent")
    .build()
)
```

Deploy to AWS Lambda and the runtime handles SYNC/ASYNC routing automatically.

---

## 📚 Examples

Explore complete examples in our repository:

- **[Basic Agent](https://github.com/CoreNovus/ainalyn-sdk/blob/master/examples/basic_agent.py)** - Simple workflow example
- **[Meeting Transcriber](https://github.com/CoreNovus/ainalyn-sdk/blob/master/examples/meeting_transcriber_agent.py)** - Multi-step COMPOSITE agent
- **[Price Monitor](https://github.com/CoreNovus/ainalyn-sdk/blob/master/examples/price_monitor_agent.py)** - ATOMIC agent with custom logic

---

## 🔧 CLI Reference

```bash
# Validate agent definition
ainalyn validate my_agent.py

# Compile to YAML
ainalyn compile my_agent.py -o agent.yaml

# Run validation with verbose output
ainalyn validate my_agent.py --verbose
```

---

## 🐛 Troubleshooting

### Common Issues

**ImportError: No module named 'ainalyn'**
```bash
pip install ainalyn-sdk
```

**ValidationError: Missing required field**
- Ensure all required fields are set in builders
- Check that `description()`, `version()`, etc. are called

**ReferenceError: Module 'xyz' not found**
- Verify module names match exactly
- Check that referenced modules are added to agent

For more help, see our [GitHub Issues](https://github.com/CoreNovus/ainalyn-sdk/issues).

---

## 📖 Documentation

- **Full Documentation**: https://docs.ainalyn.corenovus.com/
- **API Reference**: https://github.com/CoreNovus/ainalyn-sdk/blob/master/docs/api-reference.md
- **Architecture Guide**: https://github.com/CoreNovus/ainalyn-sdk/blob/master/docs/architecture.md

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](https://github.com/CoreNovus/ainalyn-sdk/blob/master/CONTRIBUTING.md) for:

- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

---

## 📄 License

[MIT License](https://github.com/CoreNovus/ainalyn-sdk/blob/master/LICENSE) - See LICENSE file for details.

---

## 📝 Changelog

See [CHANGELOG.md](https://github.com/CoreNovus/ainalyn-sdk/blob/master/CHANGELOG.md) for version history and release notes.

---

## 🆘 Support

- **Documentation**: https://docs.ainalyn.corenovus.com/
- **Report Issues**: https://github.com/CoreNovus/ainalyn-sdk/issues
- **Email**: dev@ainalyn.io

---

Built with ❤️ by the CoreNovus Team

[Website](https://ainalyn.io) • [Platform](https://platform.ainalyn.io) • [Blog](https://blog.ainalyn.io)
