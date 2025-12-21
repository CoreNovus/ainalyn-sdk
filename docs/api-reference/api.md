# API Reference

The main API functions for validating and exporting agents.

## validate()

Validates an agent definition.

```python
from ainalyn.api import validate

validate(agent)
```

**Parameters:**
- `agent` (AgentDefinition) - The agent to validate

**Returns:**
- ValidationResult - Validation results

**Raises:**
- ValidationError - If validation fails

**Example:**
```python
from ainalyn import AgentBuilder
from ainalyn.api import validate

agent = AgentBuilder("MyAgent").version("1.0.0").build()
result = validate(agent)

if result.is_valid:
    print("Valid!")
```

## export_yaml()

Exports an agent definition to YAML.

```python
from ainalyn.api import export_yaml

yaml_output = export_yaml(agent)
```

**Parameters:**
- `agent` (AgentDefinition) - The agent to export

**Returns:**
- str - YAML string

**Example:**
```python
from ainalyn import AgentBuilder
from ainalyn.api import export_yaml

agent = AgentBuilder("MyAgent").version("1.0.0").build()
yaml_str = export_yaml(agent)
print(yaml_str)
```

## compile_agent()

Validates and exports an agent definition.

```python
from ainalyn.api import compile_agent
from pathlib import Path

result = compile_agent(agent, Path("agent.yaml"))
```

**Parameters:**
- `agent` (AgentDefinition) - The agent to compile
- `output_path` (Path) - Where to save the YAML

**Returns:**
- CompilationResult - Compilation results

**Example:**
```python
from ainalyn import AgentBuilder
from ainalyn.api import compile_agent
from pathlib import Path

agent = AgentBuilder("MyAgent").version("1.0.0").build()
result = compile_agent(agent, Path("output.yaml"))

if result.is_successful:
    print(f"Saved to {result.output_path}")
```
