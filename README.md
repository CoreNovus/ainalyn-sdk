# Ainalyn SDK

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen)](https://corenovus.github.io/ainalyn-sdk/)

**Agent Definition Compiler for the Ainalyn Platform**

Ainalyn SDK helps you define, validate, and export task-oriented agents using a clean Python API. Think of it as a compiler: you describe what your agent does, the SDK validates it, and outputs a platform-ready YAML file.

> **Note**: This SDK is a **compiler, not a runtime**. It creates agent descriptions—the Ainalyn Platform handles execution.

## Why Ainalyn SDK?

- **Type-safe Builder API** - Define agents with IDE autocomplete and compile-time checks
- **Comprehensive Validation** - Catch errors before deployment
- **YAML Export** - One-line compilation to platform-ready format
- **Clean Architecture** - Well-tested, maintainable codebase

## Quick Start

### Installation

```bash
pip install ainalyn-sdk
```

### Your First Agent

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder, PromptBuilder
from ainalyn.api import validate, export_yaml

# Define a prompt
greeting_prompt = (
    PromptBuilder("greeting-prompt")
    .description("Generates a personalized greeting")
    .template("Generate a personalized greeting for {{user_name}}")
    .variables("user_name")
    .build()
)

# Define a simple agent
agent = (
    AgentBuilder("greeting-agent")
    .description("Generates personalized greetings")
    .version("1.0.0")
    .add_prompt(greeting_prompt)
    .add_workflow(
        WorkflowBuilder("greet-user")
        .description("Main greeting workflow")
        .add_node(
            NodeBuilder("generate-greeting")
            .description("Generate a personalized greeting message")
            .uses_prompt("greeting-prompt")
            .outputs("greeting")
            .build()
        )
        .entry_node("generate-greeting")
        .build()
    )
    .build()
)

# Validate and export
result = validate(agent)
if result.is_valid:
    yaml_output = export_yaml(agent)
    print(yaml_output)
```

**Output:**
```yaml
# Ainalyn Agent Definition
# This file is a description submitted to Platform Core for review.
# It does NOT execute by itself. Execution is handled by Platform Core.
#
# Local compilation does NOT equal platform execution.

name: greeting-agent
version: 1.0.0
description: Generates personalized greetings
workflows:
- name: greet-user
  description: Main greeting workflow
  entry_node: generate-greeting
  nodes:
  - name: generate-greeting
    description: Generate a personalized greeting message
    type: prompt
    reference: greeting-prompt
    outputs:
    - greeting
prompts:
- name: greeting-prompt
  description: Generates a personalized greeting
  template: Generate a personalized greeting for {{user_name}}
  variables:
  - user_name
```

### Submitting Agents to Platform

After compiling your agent, submit it directly to the Ainalyn Platform for review:

```python
from ainalyn import AgentBuilder, submit_agent, track_submission

# Build your agent
agent = (
    AgentBuilder("my-agent")
    .version("1.0.0")
    .description("My awesome agent")
    # ... add workflows, prompts, tools ...
    .build()
)

# Submit for review
result = submit_agent(agent, api_key="your_api_key")
print(f"Review ID: {result.review_id}")
print(f"Track at: {result.tracking_url}")

# Check submission status
status = track_submission(result.review_id, api_key="your_api_key")
if status.is_live:
    print(f"Agent is live: {status.marketplace_url}")
```

**Important:**
- SDK can submit but **NOT approve** - Platform Core has final authority
- Submission does **NOT** create an Execution
- Submission does **NOT** incur billing (unless platform policy states)
- Get your API key at: `https://console.ainalyn.io/api-keys`

See [examples/submit_agent_example.py](examples/submit_agent_example.py) for a complete walkthrough.

### CLI Usage

```bash
# Validate an agent definition
ainalyn validate my_agent.py

# Compile to YAML
ainalyn compile my_agent.py --output agent.yaml
```

## Documentation

**[Full Documentation](https://corenovus.github.io/ainalyn-sdk/)** - Complete guides, API reference, and examples

**Quick Links:**

- [What is an Agent?](https://corenovus.github.io/ainalyn-sdk/concepts/what-is-an-agent/) - Understand the vision
- [Installation Guide](https://corenovus.github.io/ainalyn-sdk/getting-started/installation/)
- [5-Minute Quickstart](https://corenovus.github.io/ainalyn-sdk/getting-started/quickstart/)
- [Your First Agent Tutorial](https://corenovus.github.io/ainalyn-sdk/getting-started/your-first-agent/)
- [Platform Boundaries](https://corenovus.github.io/ainalyn-sdk/concepts/platform-boundaries/)
- [Troubleshooting](https://corenovus.github.io/ainalyn-sdk/troubleshooting/)

## Examples

Check out the `examples/` directory:

- [basic_agent.py](examples/basic_agent.py) - Simple greeting agent
- [multi_workflow_agent.py](examples/multi_workflow_agent.py) - Complex data analysis agent
- [submit_agent_example.py](examples/submit_agent_example.py) - Agent submission workflow
- [price_monitor_agent.py](examples/price_monitor_agent.py) - Complete price monitoring agent

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**For newcomers**, look for issues labeled [`good first issue`](https://github.com/CoreNovus/ainalyn-sdk/labels/good%20first%20issue).

## Requirements

- Python 3.11, 3.12, or 3.13
- PyYAML >= 6.0

## License

[MIT License](LICENSE) - see LICENSE file for details.

## Support

- [Documentation](https://corenovus.github.io/ainalyn-sdk/)
- [Report Issues](https://github.com/CoreNovus/ainalyn-sdk/issues)
- [Discussions](https://github.com/CoreNovus/ainalyn-sdk/discussions)

---

Built by the CoreNovus Team
