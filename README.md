# Ainalyn SDK

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen)](https://corenovus.github.io/ainalyn-sdk/)

**Agent Definition Compiler for the Ainalyn Platform**

Ainalyn SDK helps you define, validate, and export task-oriented agents using a clean Python API. Think of it as a compiler: you describe what your agent does, the SDK validates it, and outputs a platform-ready YAML file.

> **Note**: This SDK is a **compiler, not a runtime**. It creates agent descriptions—the Ainalyn Platform handles execution.

## Why Ainalyn SDK?

- ✅ **Type-safe Builder API** - Define agents with IDE autocomplete and compile-time checks
- 📋 **Comprehensive Validation** - Catch errors before deployment
- 📦 **YAML Export** - One-line compilation to platform-ready format
- 🏗️ **Clean Architecture** - Well-tested, maintainable codebase

## Quick Start

### Installation

```bash
pip install ainalyn-sdk
```

### Your First Agent

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate, export_yaml

# Define a simple agent
agent = (
    AgentBuilder("GreetingAgent")
    .description("Generates personalized greetings")
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
print(yaml_output)
```

**Output:**
```yaml
name: GreetingAgent
version: 1.0.0
description: Generates personalized greetings
workflows:
  - name: greet_user
    nodes:
      - name: generate_greeting
        goal: Generate a personalized greeting message
```

### CLI Usage

```bash
# Validate an agent definition
ainalyn validate my_agent.py

# Compile to YAML
ainalyn compile my_agent.py --output agent.yaml
```

## Documentation

📚 **[Full Documentation](https://corenovus.github.io/ainalyn-sdk/)** - Complete guides, API reference, and examples

**Quick Links:**
- [Installation Guide](https://corenovus.github.io/ainalyn-sdk/getting-started/installation/)
- [5-Minute Quickstart](https://corenovus.github.io/ainalyn-sdk/getting-started/quickstart/)
- [Your First Agent Tutorial](https://corenovus.github.io/ainalyn-sdk/getting-started/your-first-agent/)
- [Platform Boundaries](https://corenovus.github.io/ainalyn-sdk/concepts/platform-boundaries/)
- [Troubleshooting](https://corenovus.github.io/ainalyn-sdk/troubleshooting/)

## Examples

Check out the [`examples/`](examples/) directory:
- **[basic_agent.py](examples/basic_agent.py)** - Simple greeting agent
- **[multi_workflow_agent.py](examples/multi_workflow_agent.py)** - Complex data analysis agent

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**For newcomers**, look for issues labeled [`good first issue`](https://github.com/CoreNovus/ainalyn-sdk/labels/good%20first%20issue).

## Requirements

- Python 3.11, 3.12, or 3.13
- PyYAML >= 6.0

## License

[MIT License](LICENSE) - see LICENSE file for details.

## Support

- 📖 [Documentation](https://corenovus.github.io/ainalyn-sdk/)
- 🐛 [Report Issues](https://github.com/CoreNovus/ainalyn-sdk/issues)
- 💬 [Discussions](https://github.com/CoreNovus/ainalyn-sdk/discussions)

---

Built with ❤️ by the CoreNovus Team
