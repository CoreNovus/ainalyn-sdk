# Ainalyn SDK

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen)](https://corenovus.github.io/ainalyn-sdk/)

**Agent Definition Compiler for the Ainalyn Platform**

Ainalyn SDK helps you define, validate, and export task-oriented agents using a clean Python API. Think of it as a compiler-first toolkit: you describe what your agent does, the SDK validates it, and outputs a platform-ready YAML file.

> **Note**: The SDK is **compiler-first** and includes an optional runtime wrapper for ATOMIC handlers. Platform Core still owns execution, state, and billing.

## Why Ainalyn SDK?

**Dual-Purpose Toolkit for Task-Oriented Agents:**

- **Compiler** - Define agents with type-safe Builder API, validate, and export to YAML
- **Runtime** - Deploy ATOMIC agents as Lambda functions with `@agent.atomic` decorator
- **Two Development Paths:**
  - **COMPOSITE Agents** - Build workflows visually using Builder API (graph-first)
  - **ATOMIC Agents** - Write Python functions with custom logic (code-first)
- **Production-Ready** - Comprehensive validation, clean architecture, 160+ tests

## Quick Start (5 Minutes)

### Installation

```bash
pip install ainalyn-sdk
```

### Path 1: COMPOSITE Agent (Graph-First)

Build agents using workflows and nodes:

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder, ModuleBuilder, compile_agent

# Define a module (reusable capability)
greeting_module = (
    ModuleBuilder("greeting-module")
    .description("Generates personalized greetings")
    .build()
)

# Build agent with workflow
agent = (
    AgentBuilder("greeting-agent")
    .version("1.0.0")
    .description("A simple greeting agent")
    .add_module(greeting_module)
    .add_workflow(
        WorkflowBuilder("main")
        .description("Main greeting workflow")
        .add_node(
            NodeBuilder("greet")
            .description("Generate greeting")
            .uses_module("greeting-module")
            .build()
        )
        .entry_node("greet")
        .build()
    )
    .build()
)

# Compile to YAML
result = compile_agent(agent, output_path="greeting-agent.yaml")
if result.is_valid:
    print(f"✓ Agent compiled: {result.file_path}")
else:
    print(f"✗ Validation errors: {result.errors}")
```

### Path 2: ATOMIC Agent (Code-First)

Write Python functions with custom logic:

```python
from ainalyn.runtime import agent

@agent.atomic(name="pdf-parser", version="1.0.0")
def handler(input_data: dict) -> dict:
    """Extract text from PDF files."""
    file_url = input_data["file_url"]

    # Your custom logic here
    text = extract_pdf_text(file_url)

    return {"text": text, "page_count": 10}
```

Then create the agent definition for platform submission:

```python
from ainalyn import AgentBuilder, compile_agent

agent = (
    AgentBuilder("pdf-parser")
    .version("1.0.0")
    .description("Extracts text from PDF files")
    .build()
)

compile_agent(agent, output_path="pdf-parser.yaml")
```

**Deploy:** Package handler as Lambda function → [See Runtime Deployment Guide](http://docs.ainalyn.corenovus.com/v1/guides/runtime-deployment/)

### CLI Usage

```bash
# Validate agent definition
ainalyn validate my_agent.py

# Compile to YAML
ainalyn compile my_agent.py --output agent.yaml
```

## Documentation

**[Full Documentation](http://docs.ainalyn.corenovus.com/)** - Complete guides, API reference, and examples

**Quick Links:**

- [What is an Agent?](http://docs.ainalyn.corenovus.com/v1/concepts/what-is-an-agent/) - Understand the vision
- [Installation Guide](http://docs.ainalyn.corenovus.com/v1/getting-started/installation/)
- [5-Minute Quickstart](http://docs.ainalyn.corenovus.com/v1/getting-started/quickstart/)
- [Your First Agent Tutorial](http://docs.ainalyn.corenovus.com/v1/getting-started/your-first-agent/)

## Examples

Check out the `examples/` directory:

- [basic_agent.py](examples/basic_agent.py) - Simple greeting agent
- [multi_workflow_agent.py](examples/multi_workflow_agent.py) - Complex data analysis agent
- [price_monitor_agent.py](examples/price_monitor_agent.py) - Price monitoring agent
- [meeting_transcriber_agent.py](examples/meeting_transcriber_agent.py) - Meeting transcription agent

## Contributing

We welcome contributions! See [CONTRIBUTING.md](https://github.com/CoreNovus/ainalyn-sdk/blob/master/CONTRIBUTING.md) for guidelines.

**For newcomers**, look for issues labeled [`good first issue`](https://github.com/CoreNovus/ainalyn-sdk/labels/good%20first%20issue).

## Requirements

- Python 3.11, 3.12, or 3.13
- PyYAML >= 6.0

## License

[MIT License](https://github.com/CoreNovus/ainalyn-sdk/blob/master/LICENSE) - see LICENSE file for details.

## Support

- [Documentation](http://docs.ainalyn.corenovus.com/)
- [Report Issues](https://github.com/CoreNovus/ainalyn-sdk/issues)
- [Discussions](https://github.com/CoreNovus/ainalyn-sdk/issues)

---

Built by the CoreNovus Team
