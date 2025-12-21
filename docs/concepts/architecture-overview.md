# Architecture Overview

The Ainalyn SDK is built on **Hexagonal Architecture** (also known as Ports and Adapters), ensuring clean separation of concerns and maintainability.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Ainalyn SDK                             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Layer 5: Public API & CLI                    │  │
│  │  api.py, cli.py, __init__.py                         │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │         Layer 4: Application                         │  │
│  │  Use Cases, Services                                 │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │         Layer 3: Adapters                            │  │
│  │  Primary: Builders, Errors                           │  │
│  │  Secondary: Validators, Exporters, Analyzers         │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │         Layer 2: Ports                               │  │
│  │  Inbound: Builder, Validator, Exporter Protocols     │  │
│  │  Outbound: Writer, SchemaValidator Protocols         │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │         Layer 1: Domain                              │  │
│  │  Entities: AgentDefinition, Workflow, Node, etc.     │  │
│  │  Rules: DefinitionRules, Validators                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## The Five Layers

### Layer 1: Domain (Core Business Logic)

**Location**: `ainalyn/domain/`

**Purpose**: Pure business entities and rules with NO external dependencies

**Components**:
- **Entities** (`entities/`): Immutable frozen dataclasses
  - `AgentDefinition` - The aggregate root
  - `Workflow`, `Node`, `Module`, `Prompt`, `Tool`
- **Rules** (`rules/`): Domain validation logic
  - Naming conventions
  - Circular dependency detection
  - Platform boundary enforcement

**Key Characteristics**:
- ✅ Frozen dataclasses (immutable)
- ✅ No external dependencies
- ✅ Pure Python types
- ✅ 100% type-safe

**Example**:
```python
@dataclass(frozen=True)
class AgentDefinition:
    """Agent Definition - The aggregate root.

    NOTE: This is a DESCRIPTION entity, not a runtime implementation.
    """
    name: str
    version: str
    description: str
    workflows: tuple[Workflow, ...]
    modules: tuple[Module, ...]
    prompts: tuple[Prompt, ...]
    tools: tuple[Tool, ...]
```

### Layer 2: Ports (Interface Definitions)

**Location**: `ainalyn/ports/`

**Purpose**: Define contracts between layers using Python Protocols

**Components**:
- **Inbound Ports** (`inbound/`): How external world uses the SDK
  - `Builder` - Interface for building entities
  - `Validator` - Interface for validation
  - `Exporter` - Interface for export
- **Outbound Ports** (`outbound/`): How SDK uses external services
  - `Writer` - File writing interface
  - `SchemaValidator` - Schema validation interface

**Key Characteristics**:
- ✅ Protocol-based (duck typing)
- ✅ No implementations
- ✅ Dependency Inversion Principle

**Example**:
```python
class Builder(Protocol[T]):
    """Protocol for builder pattern."""

    def build(self) -> T:
        """Build and return the entity."""
        ...
```

### Layer 3: Adapters (Implementations)

**Location**: `ainalyn/adapters/`

**Purpose**: Implement the port interfaces

**Components**:
- **Primary Adapters** (`primary/`): Entry points
  - `AgentBuilder`, `WorkflowBuilder`, `NodeBuilder`, etc.
  - `BuilderError`, `ValidationError`
- **Secondary Adapters** (`secondary/`): Infrastructure
  - `YamlExporter` - YAML export implementation
  - `SchemaValidator` - JSON Schema validation
  - `StaticAnalyzer` - Code analysis

**Key Characteristics**:
- ✅ Implements Protocol interfaces
- ✅ Handles external interactions
- ✅ Converts between layers

**Example**:
```python
class AgentBuilder:
    """Fluent builder for AgentDefinition."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._workflows: list[Workflow] = []
        # ...

    def add_workflow(self, workflow: Workflow) -> AgentBuilder:
        """Add a workflow (fluent interface)."""
        self._workflows.append(workflow)
        return self

    def build(self) -> AgentDefinition:
        """Build the AgentDefinition."""
        return AgentDefinition(
            name=self._name,
            workflows=tuple(self._workflows),
            # ...
        )
```

### Layer 4: Application (Use Cases & Services)

**Location**: `ainalyn/application/`

**Purpose**: Orchestrate domain logic and adapters

**Components**:
- `DefinitionService` - Core service coordinating operations
- **Use Cases** (`use_cases/`):
  - `ValidateDefinitionUseCase`
  - `ExportDefinitionUseCase`
  - `CompileDefinitionUseCase`

**Key Characteristics**:
- ✅ Orchestrates workflows
- ✅ No business logic (delegates to domain)
- ✅ Dependency injection

**Example**:
```python
class DefinitionService:
    """Service for agent definition operations."""

    def __init__(
        self,
        validator: Validator,
        exporter: Exporter,
    ) -> None:
        self._validator = validator
        self._exporter = exporter

    def compile(self, definition: AgentDefinition) -> str:
        """Validate and export definition."""
        self._validator.validate(definition)
        return self._exporter.export(definition)
```

### Layer 5: Public API & CLI

**Location**: `ainalyn/api.py`, `ainalyn/cli.py`, `ainalyn/__init__.py`

**Purpose**: Provide convenient entry points for users

**Components**:
- `api.py` - High-level functions (`validate()`, `export_yaml()`)
- `cli.py` - Command-line interface
- `__init__.py` - Public exports

**Key Characteristics**:
- ✅ User-friendly interfaces
- ✅ Minimal logic (delegates to layers below)
- ✅ Clear public API

**Example**:
```python
# api.py
def validate(definition: AgentDefinition) -> None:
    """Validate an agent definition."""
    service = _get_service()
    service.validate(definition)

def export_yaml(definition: AgentDefinition) -> str:
    """Export definition to YAML."""
    service = _get_service()
    return service.export_yaml(definition)
```

## Dependency Flow

Dependencies always point **inward**:

```
API/CLI
  ↓
Application
  ↓
Adapters
  ↓
Ports (interfaces)
  ↓
Domain (pure logic)
```

**Why?**: The domain layer has zero dependencies, making it:
- Easy to test
- Easy to understand
- Easy to change
- Stable and reliable

## Design Patterns

### 1. Builder Pattern

Used for entity construction:

```python
agent = (
    AgentBuilder("MyAgent")
    .description("...")
    .version("1.0.0")
    .add_workflow(...)
    .build()
)
```

### 2. Protocol Pattern (Interface Segregation)

Used for defining interfaces:

```python
class Validator(Protocol):
    def validate(self, definition: AgentDefinition) -> None: ...
```

### 3. Singleton Pattern

Used for the main service:

```python
# Module-level singleton
_service: DefinitionService | None = None

def _get_service() -> DefinitionService:
    global _service
    if _service is None:
        _service = DefinitionService(...)
    return _service
```

### 4. Immutability Pattern

All entities are frozen:

```python
@dataclass(frozen=True)
class Workflow:
    name: str
    nodes: tuple[Node, ...]  # Immutable tuple
```

### 5. Use Case Pattern

Encapsulates application logic:

```python
class ValidateDefinitionUseCase:
    def execute(self, definition: AgentDefinition) -> None:
        # Validation logic
        ...
```

## SOLID Principles

### Single Responsibility Principle (SRP)

Each class/module has one reason to change:

- `AgentBuilder`: Build agents
- `YamlExporter`: Export YAML
- `DefinitionRules`: Validate rules

### Open/Closed Principle (OCP)

Entities are frozen (closed for modification):

```python
@dataclass(frozen=True)  # Cannot be modified
class AgentDefinition:
    ...
```

### Liskov Substitution Principle (LSP)

Any `Validator` implementation works:

```python
def validate_agent(validator: Validator, agent: AgentDefinition) -> None:
    validator.validate(agent)  # Any validator works
```

### Interface Segregation Principle (ISP)

Small, focused protocols:

```python
class Builder(Protocol[T]):
    def build(self) -> T: ...

class Validator(Protocol):
    def validate(self, definition: AgentDefinition) -> None: ...
```

### Dependency Inversion Principle (DIP)

Depend on abstractions (Protocols), not concretions:

```python
class DefinitionService:
    def __init__(self, validator: Validator, exporter: Exporter):
        # Depends on protocols, not concrete classes
        ...
```

## Why Hexagonal Architecture?

### Benefits

1. **Testability**: Each layer can be tested independently
2. **Maintainability**: Changes in one layer don't cascade
3. **Flexibility**: Easy to swap implementations
4. **Clarity**: Clear separation of concerns

### Example: Swapping Exporters

Want to add JSON export? Just implement the `Exporter` protocol:

```python
class JsonExporter:
    """JSON export implementation."""

    def export(self, definition: AgentDefinition) -> str:
        # JSON export logic
        ...
```

No changes needed to:
- Domain layer
- Application layer
- API layer

## Type Safety

The SDK uses strict type checking:

```toml
# pyproject.toml
[tool.mypy]
strict = true
disallow_any_unimported = true
disallow_untyped_defs = true
```

**Benefits**:
- Catch errors at development time
- Excellent IDE support
- Self-documenting code

## Testing Strategy

### Unit Tests

Test each layer independently:

```python
def test_agent_builder():
    """Test AgentBuilder in isolation."""
    builder = AgentBuilder("TestAgent")
    agent = builder.version("1.0.0").build()
    assert agent.name == "TestAgent"
```

### Integration Tests

Test layer interactions:

```python
def test_compile_agent():
    """Test full compilation flow."""
    agent = AgentBuilder("TestAgent")....build()
    yaml_output = export_yaml(agent)
    assert "name: TestAgent" in yaml_output
```

## Package Structure

```
ainalyn/
├── domain/                    # Layer 1: Pure business logic
│   ├── entities/
│   │   ├── agent_definition.py
│   │   ├── workflow.py
│   │   ├── node.py
│   │   └── ...
│   └── rules/
│       └── definition_rules.py
│
├── ports/                     # Layer 2: Interfaces
│   ├── inbound/
│   │   ├── builder.py
│   │   ├── validator.py
│   │   └── exporter.py
│   └── outbound/
│       ├── writer.py
│       └── schema_validator.py
│
├── adapters/                  # Layer 3: Implementations
│   ├── primary/
│   │   ├── builders.py
│   │   └── errors.py
│   └── secondary/
│       ├── validators.py
│       ├── exporters.py
│       └── analyzers.py
│
├── application/               # Layer 4: Use cases
│   ├── services.py
│   └── use_cases/
│       ├── validate_definition.py
│       ├── export_definition.py
│       └── compile_definition.py
│
├── api.py                     # Layer 5: Public API
├── cli.py                     # Layer 5: CLI
└── __init__.py               # Layer 5: Exports
```

## Data Flow Example

### Building and Exporting an Agent

```
1. User calls AgentBuilder()           [Layer 5: API]
         ↓
2. AgentBuilder constructs             [Layer 3: Adapter]
         ↓
3. .build() creates AgentDefinition    [Layer 1: Domain]
         ↓
4. User calls export_yaml()            [Layer 5: API]
         ↓
5. DefinitionService orchestrates      [Layer 4: Application]
         ↓
6. YamlExporter exports                [Layer 3: Adapter]
         ↓
7. YAML string returned to user        [Layer 5: API]
```

## Further Reading

- **[Domain Layer](../contributor-guide/architecture/layer-01-domain.md)** - Detailed domain layer docs
- **[Ports Layer](../contributor-guide/architecture/layer-02-ports.md)** - Protocol definitions
- **[Adapters Layer](../contributor-guide/architecture/layer-03-adapters.md)** - Implementations
- **[Application Layer](../contributor-guide/architecture/layer-04-application.md)** - Use cases
- **[API Layer](../contributor-guide/architecture/layer-05-api-cli.md)** - Public interfaces

---

**The architecture ensures the SDK remains a focused, reliable compiler for agent definitions!** 🏗️
