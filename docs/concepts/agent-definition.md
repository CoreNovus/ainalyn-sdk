# Agent Definition

An **Agent Definition** is the complete specification of a task-oriented agent for the Ainalyn Platform. This document explains what an Agent Definition is, what it contains, and how to create one.

## What is an Agent Definition?

An Agent Definition is a **description** of an agent's structure, capabilities, and workflows. It is **NOT** an executing system—it's a blueprint that the platform uses to create executions.

```python
agent_definition = AgentDefinition(
    name="MyAgent",
    version="1.0.0",
    description="What the agent does",
    workflows=(...),   # How the agent works
    modules=(...),     # Reusable capabilities
    prompts=(...),     # LLM guidance
    tools=(...),       # External integrations
)
```

## Core Components

### 1. Agent Metadata

Every agent has basic metadata:

```python
agent = (
    AgentBuilder("TaskAgent")
    .description("Automates repetitive tasks efficiently")
    .version("2.1.0")
    .build()
)
```

**Fields**:
- **`name`** (required): Unique identifier (valid Python identifier)
- **`version`** (required): Semantic version (e.g., "1.0.0", "2.3.1")
- **`description`** (required): Human-readable description

### 2. Workflows

Workflows define the task execution logic:

```python
workflow = WorkflowBuilder("main_flow")
    .description("Primary task workflow")
    .add_node(...)
    .add_node(...)
    .build()
```

**Purpose**: Organize nodes into logical execution flows

**See**: [Workflows Guide](../guides/workflows.md)

### 3. Nodes

Nodes are the smallest units of work:

```python
node = NodeBuilder("process_data")
    .goal("Process and clean the input data")
    .description("Additional context...")
    .depends_on("load_data")
    .build()
```

**Purpose**: Represent individual sub-tasks

**See**: [Workflows Guide](../guides/workflows.md)

### 4. Modules

Modules provide reusable capabilities:

```python
module = ModuleBuilder("DataProcessor")
    .description("Reusable data processing capabilities")
    .add_capability("parse_csv")
    .add_capability("validate_schema")
    .build()
```

**Purpose**: Share common functionality across workflows

**See**: [Modules Guide](../guides/modules.md)

### 5. Prompts

Prompts guide LLM behavior:

```python
prompt = PromptBuilder("analysis_prompt")
    .template("Analyze the following data: {data}")
    .build()
```

**Purpose**: Define LLM interaction templates

### 6. Tools

Tools specify external integrations:

```python
tool = ToolBuilder("api_caller")
    .description("Calls external REST APIs")
    .add_parameter("url")
    .add_parameter("method")
    .build()
```

**Purpose**: Declare external capabilities needed

## Agent Definition Structure

Here's the complete entity structure:

```python
@dataclass(frozen=True)
class AgentDefinition:
    """Complete agent specification."""

    # Required metadata
    name: str                           # Agent identifier
    version: str                        # Semantic version
    description: str                    # What the agent does

    # Optional components (default to empty tuples)
    workflows: tuple[Workflow, ...] = field(default_factory=tuple)
    modules: tuple[Module, ...] = field(default_factory=tuple)
    prompts: tuple[Prompt, ...] = field(default_factory=tuple)
    tools: tuple[Tool, ...] = field(default_factory=tuple)
```

## Minimal Valid Agent

The absolute minimum agent definition:

```python
agent = (
    AgentBuilder("MinimalAgent")
    .description("A minimal agent")
    .version("1.0.0")
    .build()
)
```

**Note**: While valid, a useful agent needs at least one workflow!

## Complete Example

A realistic agent with all components:

```python
from ainalyn import (
    AgentBuilder,
    WorkflowBuilder,
    NodeBuilder,
    ModuleBuilder,
    PromptBuilder,
    ToolBuilder,
)

# Define a reusable module
csv_module = (
    ModuleBuilder("CSVProcessor")
    .description("CSV file processing capabilities")
    .add_capability("read_csv")
    .add_capability("validate_csv")
    .build()
)

# Define a prompt
analysis_prompt = (
    PromptBuilder("data_analysis")
    .template("Analyze this data and provide insights: {data}")
    .build()
)

# Define a tool
api_tool = (
    ToolBuilder("rest_api")
    .description("REST API integration")
    .add_parameter("endpoint")
    .build()
)

# Define workflow nodes
load_node = (
    NodeBuilder("load_data")
    .goal("Load data from CSV file")
    .build()
)

analyze_node = (
    NodeBuilder("analyze_data")
    .goal("Perform statistical analysis")
    .depends_on("load_data")
    .build()
)

report_node = (
    NodeBuilder("generate_report")
    .goal("Create analysis report")
    .depends_on("analyze_data")
    .build()
)

# Define workflow
analysis_workflow = (
    WorkflowBuilder("analyze_csv")
    .description("Load, analyze, and report on CSV data")
    .add_node(load_node)
    .add_node(analyze_node)
    .add_node(report_node)
    .build()
)

# Create complete agent
data_analyst = (
    AgentBuilder("DataAnalyst")
    .description("Automated CSV data analysis and reporting")
    .version("1.0.0")
    .add_workflow(analysis_workflow)
    .add_module(csv_module)
    .add_prompt(analysis_prompt)
    .add_tool(api_tool)
    .build()
)
```

## YAML Representation

When exported, the agent definition becomes:

```yaml
name: DataAnalyst
version: 1.0.0
description: Automated CSV data analysis and reporting

workflows:
  - name: analyze_csv
    description: Load, analyze, and report on CSV data
    nodes:
      - name: load_data
        goal: Load data from CSV file
        dependencies: []
      - name: analyze_data
        goal: Perform statistical analysis
        dependencies: [load_data]
      - name: generate_report
        goal: Create analysis report
        dependencies: [analyze_data]

modules:
  - name: CSVProcessor
    description: CSV file processing capabilities
    capabilities: [read_csv, validate_csv]

prompts:
  - name: data_analysis
    template: "Analyze this data and provide insights: {data}"

tools:
  - name: rest_api
    description: REST API integration
    parameters: [endpoint]
```

## What an Agent Definition is NOT

!!! warning "Critical Distinctions"

    An Agent Definition is **NOT**:

    - ❌ An executing process
    - ❌ A runtime system
    - ❌ An autonomous agent
    - ❌ A service or API
    - ❌ A workflow engine

    It **IS**:

    - ✅ A specification
    - ✅ A description
    - ✅ A blueprint
    - ✅ A configuration
    - ✅ A deployment artifact

## Requirements for Valid Definitions

### 1. Naming Rules

All names must be valid Python identifiers:

```python
# ✅ Valid names
"MyAgent"
"data_processor"
"agent_v2"

# ❌ Invalid names
"my-agent"       # No hyphens
"my agent"       # No spaces
"123agent"       # Cannot start with digit
```

### 2. Semantic Versioning

Versions must follow semantic versioning:

```python
# ✅ Valid versions
"1.0.0"
"2.3.1"
"0.1.0-beta"

# ❌ Invalid versions
"1.0"            # Must have three parts
"v1.0.0"         # No 'v' prefix
"latest"         # Must be specific
```

### 3. No Circular Dependencies

Workflow nodes cannot have circular dependencies:

```python
# ❌ Invalid (circular)
workflow = (
    WorkflowBuilder("circular")
    .add_node(NodeBuilder("A").depends_on("B").build())
    .add_node(NodeBuilder("B").depends_on("A").build())  # A→B→A
    .build()
)

# ✅ Valid (acyclic)
workflow = (
    WorkflowBuilder("linear")
    .add_node(NodeBuilder("A").build())
    .add_node(NodeBuilder("B").depends_on("A").build())  # A→B
    .build()
)
```

### 4. Platform Boundary Compliance

Definitions must not include forbidden patterns:

```python
# ❌ Forbidden (execution semantics)
class MyAgent:
    def execute(self): ...  # No execution methods!

# ✅ Allowed (description only)
agent = AgentBuilder("MyAgent")....build()  # Pure description
```

## The Agent as a Product

On the Ainalyn Platform, agents are **marketplace products**:

- **Discoverable**: Users can find your agent
- **Schedulable**: Users can request execution
- **Billable**: Platform charges for executions
- **Governed**: Platform enforces policies

Your Agent Definition becomes a product listing!

## Immutability

All agent definitions are **immutable** (frozen dataclasses):

```python
agent = AgentBuilder("MyAgent")....build()

# ❌ Cannot modify
agent.name = "NewName"  # Error: frozen dataclass

# ✅ Create new version
agent_v2 = (
    AgentBuilder("MyAgent")
    .version("2.0.0")  # New version
    .build()
)
```

**Why?**: Immutability ensures definitions are stable and reproducible.

## Validation

Always validate before deployment:

```python
from ainalyn.api import validate

try:
    validate(agent)
    print("✅ Valid agent definition")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")
```

**Validation checks**:
- Name format
- Version format
- No circular dependencies
- Required fields present
- Platform boundary compliance

## Best Practices

### 1. Clear Goals

Every node should have a specific, measurable goal:

```python
# ✅ Good goal
.goal("Extract all email addresses from the input text")

# ❌ Vague goal
.goal("Process data")
```

### 2. Semantic Versioning

Update versions meaningfully:

- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features
- **Patch** (1.0.0 → 1.0.1): Bug fixes

### 3. Descriptive Names

Use self-documenting names:

```python
# ✅ Clear names
NodeBuilder("validate_email_format")
WorkflowBuilder("process_customer_orders")

# ❌ Unclear names
NodeBuilder("step1")
WorkflowBuilder("main")
```

### 4. Modular Design

Reuse modules across workflows:

```python
auth_module = ModuleBuilder("Authentication")....build()

agent = (
    AgentBuilder("MyAgent")
    .add_module(auth_module)  # Reusable!
    .add_workflow(workflow1)
    .add_workflow(workflow2)  # Both can use auth_module
    .build()
)
```

### 5. Include Documentation

Add descriptions everywhere:

```python
workflow = (
    WorkflowBuilder("data_pipeline")
    .description("ETL pipeline for customer data")  # Helpful!
    .add_node(...)
    .build()
)
```

## Further Reading

- **[Builders API](../api-reference/builders.md)** - How to build definitions
- **[Validation](../guides/validation.md)** - Validating definitions
- **[Platform Boundaries](platform-boundaries.md)** - What definitions cannot include
- **[Your First Agent](../getting-started/your-first-agent.md)** - Complete tutorial

---

**An Agent Definition is your blueprint for success on the Ainalyn Platform!** 📋
