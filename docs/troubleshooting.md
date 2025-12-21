# Troubleshooting

Common issues and their solutions when using the Ainalyn SDK.

## Installation Issues

### Python Version Errors

**Problem**: Error about Python version requirement

```
ERROR: This package requires Python >=3.11
```

**Solution**: Install Python 3.11 or higher

```bash
# Check your Python version
python --version

# Install Python 3.11+ (Ubuntu/Debian)
sudo apt install python3.11

# Install Python 3.11+ (macOS with Homebrew)
brew install python@3.11

# Windows: Download from python.org
```

### Permission Denied

**Problem**: Cannot install due to permissions

```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solution**: Use a virtual environment or --user flag

```bash
# Option 1: Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install ainalyn-sdk

# Option 2: User install
pip install --user ainalyn-sdk
```

### Module Not Found

**Problem**: Cannot import ainalyn after installation

```python
ModuleNotFoundError: No module named 'ainalyn'
```

**Solution**: Ensure ainalyn is installed in the active environment

```bash
# Check if installed
pip list | grep ainalyn

# Reinstall if needed
pip uninstall ainalyn-sdk
pip install ainalyn-sdk

# Verify import works
python -c "import ainalyn; print(ainalyn.__version__)"
```

## Validation Errors

### Invalid Name Format

**Problem**: Validation fails due to invalid name

```
ValidationError: Invalid name 'my-agent': must be a valid Python identifier
```

**Solution**: Use valid Python identifiers (letters, digits, underscores)

```python
# ❌ Wrong
AgentBuilder("my-agent")
AgentBuilder("my agent")
AgentBuilder("123agent")

# ✅ Correct
AgentBuilder("my_agent")
AgentBuilder("MyAgent")
AgentBuilder("agent123")
```

### Circular Dependency Detected

**Problem**: Nodes have circular dependencies

```
ValidationError: Circular dependency detected: A → B → A
```

**Solution**: Remove circular dependencies

```python
# ❌ Wrong (circular)
workflow = (
    WorkflowBuilder("circular")
    .add_node(NodeBuilder("A").depends_on("B").build())
    .add_node(NodeBuilder("B").depends_on("A").build())
    .build()
)

# ✅ Correct (acyclic)
workflow = (
    WorkflowBuilder("acyclic")
    .add_node(NodeBuilder("A").build())
    .add_node(NodeBuilder("B").depends_on("A").build())
    .build()
)
```

### Missing Required Field

**Problem**: Required field not provided

```
ValidationError: Missing required field 'version'
```

**Solution**: Provide all required fields

```python
# ❌ Wrong (missing version)
agent = AgentBuilder("MyAgent").description("...").build()

# ✅ Correct (all required fields)
agent = (
    AgentBuilder("MyAgent")
    .description("My agent description")
    .version("1.0.0")
    .build()
)
```

### Invalid Version Format

**Problem**: Version doesn't follow semantic versioning

```
ValidationError: Invalid version format '1.0'
```

**Solution**: Use semantic versioning (major.minor.patch)

```python
# ❌ Wrong
.version("1.0")
.version("v1.0.0")
.version("latest")

# ✅ Correct
.version("1.0.0")
.version("2.3.1")
.version("0.1.0-beta")
```

## Builder Errors

### Forgot to Call .build()

**Problem**: Object is a builder, not an entity

```
TypeError: expected Workflow, got WorkflowBuilder
```

**Solution**: Always call `.build()` on builders

```python
# ❌ Wrong
workflow = WorkflowBuilder("my_workflow").add_node(...)

# ✅ Correct
workflow = WorkflowBuilder("my_workflow").add_node(...).build()
```

### Dependency on Non-Existent Node

**Problem**: Node depends on a node that doesn't exist

```
ValidationError: Dependency 'unknown_node' not found in workflow
```

**Solution**: Ensure dependency names match existing nodes

```python
# ❌ Wrong (typo in dependency)
workflow = (
    WorkflowBuilder("my_workflow")
    .add_node(NodeBuilder("step1").build())
    .add_node(NodeBuilder("step2").depends_on("step_1").build())  # Typo!
    .build()
)

# ✅ Correct
workflow = (
    WorkflowBuilder("my_workflow")
    .add_node(NodeBuilder("step1").build())
    .add_node(NodeBuilder("step2").depends_on("step1").build())
    .build()
)
```

## Export Issues

### YAML Export Fails

**Problem**: Cannot export to YAML

```
ExportError: Failed to export agent definition
```

**Solution**: Validate first, then export

```python
from ainalyn.api import validate, export_yaml

# Validate before exporting
try:
    validate(agent)
    yaml_output = export_yaml(agent)
except Exception as e:
    print(f"Error: {e}")
```

### Unicode/Encoding Errors

**Problem**: Special characters cause encoding errors

```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solution**: Specify UTF-8 encoding when writing files

```python
# ❌ Wrong (default encoding)
with open("agent.yaml", "w") as f:
    f.write(yaml_output)

# ✅ Correct (UTF-8 encoding)
with open("agent.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_output)
```

## CLI Issues

### Command Not Found

**Problem**: `ainalyn` command not found

```
bash: ainalyn: command not found
```

**Solution**: Ensure SDK is installed and PATH is correct

```bash
# Check if installed
pip show ainalyn-sdk

# Reinstall if needed
pip install --force-reinstall ainalyn-sdk

# Check PATH (ensure Scripts directory is in PATH)
which ainalyn  # Linux/macOS
where ainalyn  # Windows
```

### CLI Import Errors

**Problem**: CLI fails with import errors

```
ImportError: cannot import name 'AgentBuilder'
```

**Solution**: Reinstall the SDK

```bash
pip uninstall ainalyn-sdk
pip install ainalyn-sdk
```

## Type Checking Issues

### MyPy Errors

**Problem**: MyPy reports type errors

```
error: Argument has incompatible type "str"; expected "Workflow"
```

**Solution**: Ensure proper types are used

```python
# ❌ Wrong (passing string instead of Workflow)
agent = AgentBuilder("MyAgent").add_workflow("my_workflow").build()

# ✅ Correct (build workflow first)
workflow = WorkflowBuilder("my_workflow").build()
agent = AgentBuilder("MyAgent").add_workflow(workflow).build()
```

### Missing Type Hints

**Problem**: Type checker complains about missing hints

**Solution**: Import type definitions

```python
from __future__ import annotations
from ainalyn import AgentBuilder, Workflow
from ainalyn.domain.entities import AgentDefinition

agent: AgentDefinition = AgentBuilder("MyAgent").build()
```

## Runtime Errors

### Attempting to Execute Agent

**Problem**: Trying to call execution methods

```
AttributeError: 'AgentDefinition' has no attribute 'execute'
```

**Solution**: Remember the SDK is a compiler, not a runtime

```python
# ❌ Wrong (SDK cannot execute)
agent = AgentBuilder("MyAgent").build()
result = agent.execute()  # Method doesn't exist!

# ✅ Correct (compile to YAML for platform)
agent = AgentBuilder("MyAgent").build()
yaml_output = export_yaml(agent)
# Upload YAML to platform for execution
```

### Modifying Frozen Entities

**Problem**: Cannot modify entity after creation

```
dataclasses.FrozenInstanceError: cannot assign to field 'name'
```

**Solution**: Entities are immutable, create new ones instead

```python
# ❌ Wrong (cannot modify)
agent = AgentBuilder("MyAgent").build()
agent.name = "NewName"  # Error!

# ✅ Correct (create new agent)
agent_v2 = AgentBuilder("NewName").version("2.0.0").build()
```

## Documentation Build Issues

### MkDocs Not Found

**Problem**: Cannot build documentation

```
mkdocs: command not found
```

**Solution**: Install documentation dependencies

```bash
pip install "ainalyn-sdk[docs]"

# Or install individually
pip install mkdocs mkdocs-material mkdocstrings[python]
```

### Build Warnings

**Problem**: Documentation builds with warnings

```
WARNING: Could not find cross-reference target
```

**Solution**: Check internal links and references

```bash
# Build with strict mode to catch all issues
mkdocs build --strict
```

## Performance Issues

### Slow Validation

**Problem**: Validation takes too long for large agents

**Solution**: This is expected for complex agents with many nodes

```python
# Validation complexity grows with:
# - Number of nodes
# - Number of dependencies
# - Complexity of rules

# For very large agents, validation may take several seconds
# This is normal and ensures definition correctness
```

## Getting More Help

### Check the Documentation

- [Installation Guide](getting-started/installation.md)
- [Quickstart](getting-started/quickstart.md)
- [Platform Boundaries](concepts/platform-boundaries.md)
- [API Reference](api-reference/builders/agent-builder.md)

### Report Issues

If you encounter a bug:

1. **Check existing issues**: [GitHub Issues](https://github.com/ainalyn/ainalyn-sdk/issues)
2. **Create a minimal reproduction**: Smallest code that shows the problem
3. **Include details**:
   - SDK version (`pip show ainalyn-sdk`)
   - Python version (`python --version`)
   - Operating system
   - Error messages (full traceback)
   - Expected vs actual behavior

### Community Support

- **GitHub Discussions**: [Ask questions](https://github.com/ainalyn/ainalyn-sdk/discussions)
- **Email**: dev@ainalyn.io

## Debug Checklist

When something goes wrong:

- [ ] Is Python 3.11+ installed?
- [ ] Is ainalyn-sdk installed? (`pip show ainalyn-sdk`)
- [ ] Are you in the correct virtual environment?
- [ ] Did you call `.build()` on all builders?
- [ ] Are all required fields provided?
- [ ] Are names valid Python identifiers?
- [ ] Is the version in semantic format?
- [ ] Are there any circular dependencies?
- [ ] Did you validate before exporting?
- [ ] Are file encodings set to UTF-8?

---

**Still stuck?** Don't hesitate to reach out via GitHub Issues or email!
