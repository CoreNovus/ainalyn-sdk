# Builders API

Builders provide a fluent API for creating agent definitions.

## AgentBuilder

Creates an agent definition.

```python
from ainalyn import AgentBuilder

agent = (
    AgentBuilder("MyAgent")
    .description("What the agent does")
    .version("1.0.0")
    .add_workflow(workflow)
    .build()
)
```

**Methods:**

- `.description(text)` - Set agent description
- `.version(version)` - Set version (e.g., "1.0.0")
- `.add_workflow(workflow)` - Add a workflow
- `.add_module(module)` - Add a reusable module
- `.build()` - Create the AgentDefinition

## WorkflowBuilder

Creates a workflow.

```python
from ainalyn import WorkflowBuilder, NodeBuilder

workflow = (
    WorkflowBuilder("main_flow")
    .description("Main workflow")
    .add_node(
        NodeBuilder("task1")
        .goal("Complete task 1")
        .build()
    )
    .entry_node("task1")
    .build()
)
```

**Methods:**

- `.description(text)` - Set workflow description
- `.add_node(node)` - Add a node to this workflow
- `.entry_node(name)` - Set which node starts the workflow
- `.build()` - Create the Workflow

## NodeBuilder

Creates a node (task unit).

```python
from ainalyn import NodeBuilder, NodeType

node = (
    NodeBuilder("my_task")
    .goal("What this task accomplishes")
    .description("Optional details")
    .node_type(NodeType.TASK)
    .outputs(["result_data"])
    .depends_on("previous_task")
    .build()
)
```

**Methods:**

- `.goal(text)` - Set the task goal (required)
- `.description(text)` - Add optional description
- `.node_type(type)` - Set type (TASK, MODULE, SUBWORKFLOW)
- `.outputs(list)` - Define output names
- `.depends_on(*names)` - Set dependencies on other nodes
- `.build()` - Create the Node

## ModuleBuilder

Creates a reusable module.

```python
from ainalyn import ModuleBuilder

module = (
    ModuleBuilder("http-client")
    .description("HTTP request module")
    .input_schema({"type": "object", "properties": {...}})
    .output_schema({"type": "object", "properties": {...}})
    .build()
)
```

**Methods:**

- `.description(text)` - Set module description
- `.input_schema(schema)` - Define input JSON Schema
- `.output_schema(schema)` - Define output JSON Schema
- `.build()` - Create the Module

## PromptBuilder

Creates an LLM prompt template.

```python
from ainalyn import PromptBuilder

prompt = (
    PromptBuilder("greeting")
    .template("Hello {name}!")
    .build()
)
```

**Methods:**

- `.template(text)` - Set prompt template with placeholders
- `.build()` - Create the Prompt

## ToolBuilder

Creates a tool definition.

```python
from ainalyn import ToolBuilder

tool = (
    ToolBuilder("calculator")
    .description("Math operations")
    .build()
)
```

**Methods:**

- `.description(text)` - Set tool description
- `.build()` - Create the Tool

## Common Patterns

**Always call .build()**
```python
# ✅ Correct
node = NodeBuilder("task").goal("Do something").build()

# ❌ Wrong - missing .build()
node = NodeBuilder("task").goal("Do something")
```

**Chain methods**
```python
agent = (
    AgentBuilder("MyAgent")
    .version("1.0.0")
    .description("My agent")
    .add_workflow(workflow)
    .build()
)
```

**Dependencies**
```python
workflow = (
    WorkflowBuilder("process")
    .add_node(NodeBuilder("step1").goal("First step").build())
    .add_node(
        NodeBuilder("step2")
        .goal("Second step")
        .depends_on("step1")  # Runs after step1
        .build()
    )
    .build()
)
```
