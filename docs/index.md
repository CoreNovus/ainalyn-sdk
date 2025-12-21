# Ainalyn SDK Documentation

Welcome to the **Ainalyn SDK** documentation! The Ainalyn SDK is an **Agent Definition Compiler** that helps you define task-oriented agents for the Ainalyn Platform.

!!! warning "Critical Understanding: SDK ≠ Runtime"
    The Ainalyn SDK is a **compiler**, not a runtime execution engine. It provides tools to **describe** agents, not to execute them. Execution authority belongs solely to the Ainalyn Platform.

## What is Ainalyn SDK?

The Ainalyn SDK enables developers to:

- **Define** task-oriented agents using a clean, type-safe Python API
- **Validate** agent definitions against platform requirements
- **Export** definitions to YAML format for platform deployment
- **Compile** complete agent specifications ready for the marketplace

Think of it as a **Domain-Specific Language (DSL)** for agent descriptions, similar to how Terraform describes infrastructure or Kubernetes YAML describes deployments.

## Key Features

### 🏗️ **Clean Hexagonal Architecture**
Built on solid software engineering principles with clear separation of concerns across domain, ports, adapters, and application layers.

### 🔒 **Type-Safe API**
Full type hints with mypy strict mode compliance ensure compile-time safety and excellent IDE support.

### 🚀 **Fluent Builder Pattern**
Intuitive, chainable APIs make agent definition both powerful and pleasant to use.

### ✅ **Comprehensive Validation**
Built-in rules ensure your agent definitions comply with platform boundaries and best practices.

### 📦 **YAML Export**
Compile your agent definitions to clean, validated YAML ready for platform deployment.

### 🧪 **Testable Design**
Immutable entities and clear interfaces make your agent definitions easy to test.

## Quick Example

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder

# Define a simple data analysis agent
agent = (
    AgentBuilder("DataAnalyst")
    .description("Analyzes CSV data and generates insights")
    .version("1.0.0")
    .add_workflow(
        WorkflowBuilder("analyze_data")
        .add_node(
            NodeBuilder("load_csv")
            .goal("Load and validate CSV file")
            .build()
        )
        .add_node(
            NodeBuilder("analyze")
            .goal("Perform statistical analysis")
            .depends_on("load_csv")
            .build()
        )
        .build()
    )
    .build()
)

# Validate and export
from ainalyn.api import validate, export_yaml

validate(agent)  # Ensures compliance with platform rules
yaml_output = export_yaml(agent)  # Ready for deployment
```

## Documentation Structure

### For SDK Users

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting Started**

    ---

    New to Ainalyn SDK? Start here to install the SDK and build your first agent in minutes.

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)
    [:octicons-arrow-right-24: Quickstart](getting-started/quickstart.md)
    [:octicons-arrow-right-24: Your First Agent](getting-started/your-first-agent.md)

-   :material-lightbulb:{ .lg .middle } **Core Concepts**

    ---

    Understand the foundational concepts behind Ainalyn SDK and the platform boundaries.

    [:octicons-arrow-right-24: Platform Boundaries](concepts/platform-boundaries.md)
    [:octicons-arrow-right-24: Compiler vs Runtime](concepts/compiler-not-runtime.md)
    [:octicons-arrow-right-24: Architecture Overview](concepts/architecture-overview.md)

-   :material-book-open-variant:{ .lg .middle } **User Guide**

    ---

    Detailed guides on building agents, workflows, nodes, and more.

    [:octicons-arrow-right-24: Using Builder API](user-guide/building-agents/using-builder-api.md)
    [:octicons-arrow-right-24: Validation](user-guide/validation.md)
    [:octicons-arrow-right-24: Exporting](user-guide/exporting.md)

-   :material-code-braces:{ .lg .middle } **API Reference**

    ---

    Complete API documentation for all builders, entities, validators, and exporters.

    [:octicons-arrow-right-24: Builders](api-reference/builders/agent-builder.md)
    [:octicons-arrow-right-24: Entities](api-reference/entities/agent-definition.md)
    [:octicons-arrow-right-24: CLI](api-reference/cli.md)

</div>

### For SDK Contributors

<div class="grid cards" markdown>

-   :material-code-block-tags:{ .lg .middle } **Architecture**

    ---

    Deep dive into the hexagonal architecture and layer-by-layer design.

    [:octicons-arrow-right-24: Hexagonal Architecture](contributor-guide/architecture/hexagonal-architecture.md)
    [:octicons-arrow-right-24: Domain Layer](contributor-guide/architecture/layer-01-domain.md)
    [:octicons-arrow-right-24: All Layers](contributor-guide/architecture/layer-02-ports.md)

-   :material-hammer-wrench:{ .lg .middle } **Development**

    ---

    Everything you need to contribute to the Ainalyn SDK project.

    [:octicons-arrow-right-24: Development Setup](contributor-guide/development-setup.md)
    [:octicons-arrow-right-24: Coding Standards](contributor-guide/coding-standards.md)
    [:octicons-arrow-right-24: Testing Guide](contributor-guide/testing-guide.md)

</div>

## Platform Boundaries (Critical)

!!! danger "What the SDK Cannot Do"
    The Ainalyn SDK **CANNOT** and **MUST NOT**:

    - ❌ Execute agents or workflows
    - ❌ Make decisions about retry, timeout, or fallback strategies
    - ❌ Calculate billing or pricing
    - ❌ Act as an autonomous AI agent
    - ❌ Generate `executionId` or manage execution state

    The SDK is a **description compiler** only. All execution authority belongs to the Ainalyn Platform.

!!! success "What the SDK Can Do"
    The Ainalyn SDK **CAN** and **SHOULD**:

    - ✅ Define agent structures and workflows
    - ✅ Validate definitions against rules
    - ✅ Export to platform-compatible YAML
    - ✅ Provide local development tools (test utilities)
    - ✅ Offer type-safe APIs for agent construction

## Getting Help

- **📖 Documentation**: You're reading it! Explore the sections above.
- **🐛 Issues**: Found a bug? [Report it on GitHub](https://github.com/ainalyn/ainalyn-sdk/issues)
- **💬 Discussions**: Have questions? Join our [GitHub Discussions](https://github.com/ainalyn/ainalyn-sdk/discussions)
- **📧 Contact**: Reach out to dev@ainalyn.io for support

## License

The Ainalyn SDK is released under the [MIT License](https://github.com/ainalyn/ainalyn-sdk/blob/master/LICENSE).

---

**Ready to start?** Head to [Installation](getting-started/installation.md) to begin your journey! 🚀
