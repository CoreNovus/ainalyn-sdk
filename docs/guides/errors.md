# Error Handling

Common errors when building agents and how to fix them.

## Builder Errors

### MissingRequiredFieldError

**What it means:** You forgot to set a required field before calling `.build()`.

```python
# ❌ Error
agent = AgentBuilder("MyAgent").build()
# MissingRequiredFieldError: Required field 'version' is not set

# ✅ Fix
agent = AgentBuilder("MyAgent").version("1.0.0").build()
```

**Required fields:**
- **AgentBuilder**: `name`, `version`
- **WorkflowBuilder**: `name`
- **NodeBuilder**: `name`, `goal`

### InvalidValueError

**What it means:** The value doesn't meet the requirements.

```python
# ❌ Error - invalid name format
agent = AgentBuilder("My Agent").build()
# InvalidValueError: Invalid value for 'name': 'My Agent'

# ✅ Fix - use valid format
agent = AgentBuilder("MyAgent").build()
```

**Naming rules:**
- Start with lowercase letter or uppercase letter
- Use letters, numbers, underscores, or hyphens
- No spaces, no special characters

**Valid names:**
```python
"MyAgent"        # ✅ CamelCase
"my_agent"       # ✅ snake_case
"agent-v2"       # ✅ With hyphens
"agent123"       # ✅ With numbers
```

**Invalid names:**
```python
"my agent"       # ❌ Space
"my@agent"       # ❌ Special char
"123agent"       # ❌ Starts with number
```

### InvalidReferenceError

**What it means:** A node references a module/prompt/tool that doesn't exist.

```python
# ❌ Error
workflow = (
    WorkflowBuilder("main")
    .add_node(
        NodeBuilder("task1")
        .node_type(NodeType.MODULE)
        .reference("http-client")  # Module doesn't exist!
        .build()
    )
    .build()
)

# ✅ Fix - define the module first
module = ModuleBuilder("http-client").build()

agent = (
    AgentBuilder("MyAgent")
    .version("1.0.0")
    .add_module(module)  # Add module to agent
    .add_workflow(workflow)
    .build()
)
```

### DuplicateNameError

**What it means:** Two items have the same name in the same scope.

```python
# ❌ Error - duplicate node names
workflow = (
    WorkflowBuilder("main")
    .add_node(NodeBuilder("task").goal("First").build())
    .add_node(NodeBuilder("task").goal("Second").build())  # Duplicate!
    .build()
)

# ✅ Fix - use unique names
workflow = (
    WorkflowBuilder("main")
    .add_node(NodeBuilder("task1").goal("First").build())
    .add_node(NodeBuilder("task2").goal("Second").build())
    .build()
)
```

### EmptyCollectionError

**What it means:** A required collection is empty.

```python
# ❌ Error - workflow has no nodes
workflow = WorkflowBuilder("main").build()
# EmptyCollectionError: Workflow 'main' has no nodes

# ✅ Fix - add at least one node
workflow = (
    WorkflowBuilder("main")
    .add_node(NodeBuilder("task1").goal("Do something").build())
    .build()
)
```

## Validation Errors

### CircularDependencyError

**What it means:** Nodes depend on each other in a loop.

```python
# ❌ Error - A depends on B, B depends on A
workflow = (
    WorkflowBuilder("main")
    .add_node(NodeBuilder("A").goal("Task A").depends_on("B").build())
    .add_node(NodeBuilder("B").goal("Task B").depends_on("A").build())
    .build()
)
# ValidationError: Circular dependency detected: A → B → A

# ✅ Fix - remove the circular dependency
workflow = (
    WorkflowBuilder("main")
    .add_node(NodeBuilder("A").goal("Task A").build())
    .add_node(NodeBuilder("B").goal("Task B").depends_on("A").build())
    .build()
)
```

### InvalidDependencyError

**What it means:** A node depends on a non-existent node.

```python
# ❌ Error
workflow = (
    WorkflowBuilder("main")
    .add_node(
        NodeBuilder("task1")
        .goal("Do something")
        .depends_on("task0")  # task0 doesn't exist!
        .build()
    )
    .build()
)

# ✅ Fix - ensure dependency exists
workflow = (
    WorkflowBuilder("main")
    .add_node(NodeBuilder("task0").goal("First task").build())
    .add_node(
        NodeBuilder("task1")
        .goal("Do something")
        .depends_on("task0")  # Now it exists
        .build()
    )
    .build()
)
```

## Catching Errors

### Try-Catch Pattern

```python
from ainalyn import AgentBuilder, BuilderError
from ainalyn.api import validate

try:
    agent = (
        AgentBuilder("MyAgent")
        .version("1.0.0")
        .build()
    )
    validate(agent)
    print("✅ Success!")

except BuilderError as e:
    print(f"❌ Build error: {e.message}")

except Exception as e:
    print(f"❌ Error: {e}")
```

### Specific Error Types

```python
from ainalyn import (
    MissingRequiredFieldError,
    InvalidValueError,
    DuplicateNameError
)

try:
    agent = AgentBuilder("MyAgent").build()

except MissingRequiredFieldError as e:
    print(f"Missing: {e.field_name}")
    print(f"In: {e.builder_type}")

except InvalidValueError as e:
    print(f"Invalid {e.field_name}: {e.value}")
    print(f"Rule: {e.constraint}")

except DuplicateNameError as e:
    print(f"Duplicate {e.entity_type}: {e.name}")
```

## Common Patterns

### Progressive Building

Build complex agents step-by-step to catch errors early:

```python
# Create nodes first
node1 = NodeBuilder("task1").goal("First task").build()
node2 = NodeBuilder("task2").goal("Second task").depends_on("task1").build()

# Create workflow
workflow = (
    WorkflowBuilder("main")
    .add_node(node1)
    .add_node(node2)
    .build()
)

# Create agent
agent = (
    AgentBuilder("MyAgent")
    .version("1.0.0")
    .add_workflow(workflow)
    .build()
)

# Validate
validate(agent)
```

### Validation Before Export

Always validate before exporting:

```python
from ainalyn.api import validate, export_yaml

try:
    # Validate first
    validate(agent)

    # Then export
    yaml_output = export_yaml(agent)

    # Save to file
    with open("agent.yaml", "w") as f:
        f.write(yaml_output)

    print("✅ Exported successfully!")

except Exception as e:
    print(f"❌ Failed: {e}")
```

## Quick Reference

| Error | Cause | Fix |
|-------|-------|-----|
| MissingRequiredFieldError | Forgot to set field | Call `.field(value)` |
| InvalidValueError | Wrong value format | Use valid format |
| InvalidReferenceError | Reference doesn't exist | Define the resource first |
| DuplicateNameError | Same name used twice | Use unique names |
| EmptyCollectionError | Empty nodes/workflows | Add at least one item |
| CircularDependencyError | Circular dependencies | Remove the loop |

## Getting Help

If you encounter an error not listed here:

1. Read the error message carefully
2. Check the [API reference](../api-reference/builders.md)
3. Review the [guides](validation.md)
4. [Report an issue](https://github.com/CoreNovus/ainalyn-sdk/issues)
