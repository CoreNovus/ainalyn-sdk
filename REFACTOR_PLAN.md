# Hexagonal Architecture Refactoring Plan (REVISED)

**Version**: 2.0 - Updated based on comprehensive review
**Review Document**: See `REFACTOR_PLAN_REVIEW.md` for detailed analysis
**Status**: Ready for execution

---

## Overview

This document outlines the refactoring plan to strictly enforce hexagonal architecture principles based on:
1. Analysis in `hex-arch.md`
2. Platform constitutional documents in `rule-docs/`
3. Comprehensive architectural review

**Key Constitutional Requirements**:
- SDK is a Compiler, NOT a Runtime (per `Agent Definition Compiler & Runtime Forbidden Zone.md`)
- SDK must warn: "Local validation ≠ Platform execution"
- All execution authority belongs to Platform Core
- No execution/billing semantics in SDK

---

## Current Violations

### 1. Builders Misclassified
**Current**: `adapters/primary/builders.py`
**Problem**: Builders are entry-point DSL (inbound adapter), not business orchestration
**Impact**: Confusion about what belongs in application vs adapter layers

### 2. Ports Use Tool Names Instead of Use Case Names
**Current**: `IDefinitionBuilder`, `IDefinitionValidator`, `IDefinitionExporter`
**Problem**: Ports should express what the core needs, not how it's implemented
**Impact**: Ports become utility interfaces instead of business capability contracts

### 3. Validation Responsibility Overlap
**Current**: Validation logic in Domain, Ports, and Adapters
**Problem**: Unclear which layer is authoritative for validation rules
**Impact**: Rule changes require modifications in multiple places

### 4. Application Layer Has Concrete Dependencies
**Current**: `DefinitionService` directly instantiates `SchemaValidator`, `StaticAnalyzer`, `YamlExporter`
**Problem**: Application layer depends on specific adapter implementations
**Impact**: Hard to test, hard to swap implementations

### 5. Errors in Adapter Layer
**Current**: `adapters/primary/errors.py` contains domain errors
**Problem**: Domain errors should live in domain layer; names sound like execution errors
**Impact**: Core domain concepts depend on adapter layer; developers may confuse SDK errors with platform execution errors

### 6. Missing Infrastructure Layer
**Current**: No infrastructure/wiring layer
**Problem**: Nowhere to instantiate and wire concrete dependencies
**Impact**: Dependency injection can't be implemented properly

### 7. Missing Platform Boundary Warnings
**Current**: No explicit warnings that SDK validation ≠ Platform execution
**Problem**: Violates constitutional requirement (Section 7 of Compiler & Runtime Forbidden Zone)
**Impact**: Developers may assume local validation = platform will execute

### 8. Public API Exposes Too Much Internal Structure
**Current**: `__init__.py` exports use cases, adapters, and all error types
**Problem**: Leaks internal implementation details
**Impact**: Users depend on internal structure, making refactoring harder

---

## Refactoring Strategy

### Phase 0: Add Infrastructure Layer (NEW)

**Actions**:
1. Create `infrastructure/` directory
2. Create `infrastructure/service_factory.py` for dependency wiring
3. Update `api.py` to use factory

**New Files**:
```python
# infrastructure/service_factory.py
from ainalyn.adapters.outbound import (
    SchemaValidator,
    StaticAnalyzer,
    YamlSerializer,
    FileWriter,
)
from ainalyn.application import DefinitionService

def create_default_service() -> DefinitionService:
    """
    Create DefinitionService with default adapter implementations.

    This factory isolates the wiring of concrete adapters to ports.
    Advanced users can create custom services with their own adapters.
    """
    return DefinitionService(
        schema_validator=SchemaValidator(),
        static_analyzer=StaticAnalyzer(),
        serializer=YamlSerializer(),
        writer=FileWriter(),
    )
```

**Rationale**: Infrastructure layer handles framework concerns and dependency wiring, keeping application layer clean.

---

### Phase 1: Domain Errors with Corrected Naming

**Actions**:
1. Create `domain/errors.py` with compile-time emphasis
2. Add constitutional warnings to all docstrings
3. Update error naming to avoid execution semantics

**Structure**:
```python
# domain/errors.py
class DomainError(Exception):
    """Base for all domain-level errors."""

class DefinitionError(DomainError):
    """
    Base error for Agent Definition compilation issues.

    IMPORTANT: These are compile-time/description-time errors from the SDK.
    They indicate issues with the Agent Definition structure, not execution failures.

    Platform Core may apply additional validation during submission.
    SDK validation success does NOT guarantee platform execution.
    """

class MissingFieldError(DefinitionError):
    """Required field missing in definition."""

class InvalidFormatError(DefinitionError):
    """Field value doesn't match required format."""

class ReferenceError(DefinitionError):
    """Invalid reference within definition."""

class DuplicateError(DefinitionError):
    """Duplicate names within scope."""

class EmptyCollectionError(DefinitionError):
    """Required collection is empty."""

class CyclicDependencyError(DefinitionError):
    """Workflow contains cycles (not a DAG)."""

class UnreachableNodeError(DefinitionError):
    """Node unreachable from entry node."""
```

**Public API Exposure** (in `__init__.py`):
```python
from ainalyn.domain.errors import DefinitionError  # Base only

__all__ = [
    "DefinitionError",  # Users catch this base
    # DO NOT export specific error types
]
```

**Rationale**:
- Emphasizes these are compile-time errors, not execution errors
- Prevents confusion with platform execution failures
- Aligns with constitutional requirement that SDK ≠ Runtime

---

### Phase 2: Refactor Ports to Use-Case Based Naming

**Current Structure**:
```
ports/inbound/
  - builder.py (IDefinitionBuilder)
  - validator.py (IDefinitionValidator)
  - exporter.py (IDefinitionExporter)

ports/outbound/
  - schema_validator.py (ISchemaValidator)
  - writer.py (IWriter)
```

**New Structure**:
```
application/ports/
  inbound/
    - compile_agent_definition.py (ICompileAgentDefinition)
    - validate_agent_definition.py (IValidateAgentDefinition)
    - export_agent_definition.py (IExportAgentDefinition)

  outbound/
    - definition_schema_validation.py (IDefinitionSchemaValidator)
    - definition_static_analysis.py (IDefinitionAnalyzer)
    - definition_serialization.py (IDefinitionSerializer)
    - definition_persistence.py (IDefinitionWriter)
```

**Example Port Interface**:
```python
# application/ports/outbound/definition_schema_validation.py
class IDefinitionSchemaValidator(Protocol):
    """
    Outbound port for validating Agent Definition schemas.

    This port abstracts the capability to validate that an Agent Definition
    conforms to structural requirements. Implementations may use JSON Schema,
    custom validators, or other mechanisms.
    """

    def validate_schema(
        self,
        definition: AgentDefinition
    ) -> tuple[ValidationError, ...]:
        """
        Validate Agent Definition structure.

        Returns tuple of validation errors (empty if valid).
        """
        ...
```

**Rationale**:
- Port names emphasize business intent (what) over implementation (how)
- Always include "AgentDefinition" or "Definition" to clarify domain
- Inbound ports represent use cases; outbound ports represent needed capabilities

---

### Phase 3: Builders Stay as Inbound Adapters (CORRECTED)

**Actions**:
1. **DO NOT** move builders to application layer
2. Keep builders in `adapters/inbound/builders/`
3. Extract construction validation logic to domain entity methods
4. Builders become thin DSL layer over domain entities

**Corrected Structure**:
```
adapters/inbound/builders/
  - agent_builder.py
  - workflow_builder.py
  - node_builder.py
  - module_builder.py
  - prompt_builder.py
  - tool_builder.py
```

**Separation of Concerns**:
```python
# domain/entities/agent_definition.py
@dataclass(frozen=True)
class AgentDefinition:
    name: str
    version: str
    description: str
    workflows: tuple[Workflow, ...]
    # ...

    def __post_init__(self) -> None:
        """Validate domain rules during construction."""
        if not DefinitionRules.is_valid_name(self.name):
            raise InvalidFormatError("name", self.name, "must match [a-z0-9-]+")
        if not DefinitionRules.is_valid_version(self.version):
            raise InvalidFormatError("version", self.version, "must be semver")
        # ... other domain validations

# adapters/inbound/builders/agent_builder.py
class AgentBuilder:
    """
    Fluent builder DSL for Agent Definitions.

    This builder provides a developer-friendly API for constructing
    Agent Definition entities. It's a thin wrapper over domain entities.

    IMPORTANT: This builder creates descriptions only. Building an
    agent definition locally does NOT mean the platform will execute it.
    Platform Core applies additional governance and security checks.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._version: str | None = None
        # ... other fields

    def build(self) -> AgentDefinition:
        """Build immutable AgentDefinition."""
        if self._version is None:
            raise MissingFieldError("version", "AgentBuilder")

        # Domain entity validates itself
        return AgentDefinition(
            name=self._name,
            version=self._version,
            description=self._description or "",
            workflows=tuple(self._workflows),
            # ...
        )
```

**Rationale**:
- Builders are **entry points** (inbound adapters), not business logic
- They translate developer DSL → domain entities
- Domain entities enforce their own rules
- Clear separation: DSL (adapter) vs validation (domain)

---

### Phase 4: Implement Dependency Injection

**Current** (`services.py`):
```python
def __init__(self):
    self._schema_validator = SchemaValidator()  # ❌ Concrete dependency
    self._static_analyzer = StaticAnalyzer()    # ❌ Concrete dependency
    self._yaml_exporter = YamlExporter()        # ❌ Concrete dependency
```

**New** (`services.py`):
```python
def __init__(
    self,
    schema_validator: IDefinitionSchemaValidator,
    static_analyzer: IDefinitionAnalyzer,
    serializer: IDefinitionSerializer,
    writer: IDefinitionWriter | None = None,
):
    """
    Initialize DefinitionService with dependencies.

    Args:
        schema_validator: Port for schema validation
        static_analyzer: Port for static analysis
        serializer: Port for YAML serialization
        writer: Optional port for file writing
    """
    self._schema_validator = schema_validator
    self._static_analyzer = static_analyzer
    self._serializer = serializer
    self._writer = writer
```

**Updated `api.py`**:
```python
from ainalyn.infrastructure.service_factory import create_default_service

_service: DefinitionService | None = None

def _get_service() -> DefinitionService:
    """Get or create module-level service with default wiring."""
    global _service
    if _service is None:
        _service = create_default_service()
    return _service
```

**Rationale**:
- Application depends on abstractions (ports), not concrete adapters
- Infrastructure layer handles wiring
- Easy to test with mock implementations
- Users can create custom services with their own adapters

---

### Phase 5: Add Platform Boundary Warnings (CONSTITUTIONAL REQUIREMENT)

**Required Changes**:

1. **ValidationResult** docstring:
```python
@dataclass(frozen=True)
class ValidationResult:
    """
    Result of Agent Definition validation.

    ⚠️  CRITICAL PLATFORM BOUNDARY WARNING ⚠️

    SDK validation success does NOT guarantee platform execution.
    The Ainalyn Platform applies additional checks:
    - Governance policies
    - Security scanning
    - Resource quota validation
    - Marketplace compliance

    This validation only ensures the definition is structurally
    and semantically correct according to SDK rules.

    Per platform constitution: "Local compilation ≠ Platform execution"
    """
    errors: tuple[ValidationError, ...]

    @property
    def is_valid(self) -> bool:
        """
        Check if SDK validation passed.

        IMPORTANT: Passing SDK validation does NOT mean:
        - Platform will accept the definition
        - Platform will execute the agent
        - Agent will be listed in marketplace

        Platform Core has final authority over all executions.
        """
        return not any(e.severity == Severity.ERROR for e in self.errors)
```

2. **YAML Export Header**:
```python
# adapters/outbound/yaml_serializer.py
YAML_HEADER = """# Ainalyn Agent Definition
# This file is a DESCRIPTION submitted to Platform Core for review.
# It does NOT execute by itself. Execution is handled exclusively by Platform Core.
#
# ⚠️  CRITICAL BOUNDARY WARNING ⚠️
# - SDK validation passed ≠ Platform will execute this definition
# - Platform performs additional governance, security, and resource checks
# - Platform Core has sole authority over execution, billing, and lifecycle
#
# Local compilation does NOT equal platform execution.
# See: https://docs.ainalyn.io/sdk/platform-boundaries/
"""
```

3. **Builder Docstrings**:
```python
class AgentBuilder:
    """
    Fluent builder for Agent Definitions.

    ⚠️  SDK BOUNDARY WARNING ⚠️

    This builder creates DESCRIPTIONS of agents, not executable agents.
    Building a definition does NOT mean:
    - The agent will run locally
    - The platform will execute it
    - Billing will occur

    All execution authority belongs to Platform Core.
    The SDK is a compiler, not a runtime.
    """
```

**Rationale**: Constitutional requirement from `Agent Definition Compiler & Runtime Forbidden Zone.md` Section 7.

---

### Phase 6: Clarify Validation Boundaries

**Domain Validation** (in `domain/entities/` and `domain/rules/`):
- Structural integrity (DAG, unique names, required fields)
- Semantic correctness (valid references within definition)
- Business rules (naming patterns, version formats)
- **Authority**: Domain rules are final for definition structure

**Adapter Validation** (in `adapters/inbound/`):
- Input format validation (JSON schema, YAML syntax)
- Request DTO validation
- CLI argument validation
- **Authority**: Guards against malformed input

**Application Validation** (in `application/use_cases/`):
- Orchestrates domain validation via domain rules
- Orchestrates schema validation via outbound port
- Combines results into ValidationResult
- **Authority**: Coordinates validation, doesn't define rules

**Rationale**: Single source of truth (domain) with clear delegation.

---

### Phase 7: Reduce Public API Surface

**Current Problem** (`__init__.py` exports 40+ items):
```python
# ❌ Too much exposure
"SchemaValidator",
"StaticAnalyzer",
"YamlExporter",
"ValidateDefinitionUseCase",
"ExportDefinitionUseCase",
# ... all error types ...
```

**Corrected Public API**:
```python
"""
Ainalyn SDK - Agent Definition Compiler.

⚠️  SDK BOUNDARY WARNING ⚠️
This SDK creates descriptions of agents, not executable agents.
All execution authority belongs to Platform Core.
See: https://docs.ainalyn.io/sdk/platform-boundaries/
"""

__all__ = [
    # === HIGH-LEVEL API (Primary Interface) ===
    "validate",
    "export_yaml",
    "compile_agent",

    # === BUILDERS (Developer DSL) ===
    "AgentBuilder",
    "WorkflowBuilder",
    "NodeBuilder",
    "ModuleBuilder",
    "PromptBuilder",
    "ToolBuilder",

    # === DOMAIN ENTITIES (For type hints) ===
    "AgentDefinition",
    "Workflow",
    "Node",
    "Module",
    "Prompt",
    "Tool",
    "NodeType",

    # === RESULTS & VALIDATION ===
    "CompilationResult",
    "ValidationResult",
    "ValidationError",  # Port type, not domain error
    "Severity",

    # === ERRORS (Base only) ===
    "DefinitionError",  # Users catch this

    # === DOMAIN RULES (Advanced usage) ===
    "DefinitionRules",

    # === SERVICE (For custom DI) ===
    "DefinitionService",

    # === VERSION ===
    "__version__",
]

# DO NOT EXPORT:
# - Use cases (internal)
# - Adapters (internal)
# - Ports (internal)
# - Specific error subclasses (users catch DefinitionError)
```

**Rationale**: Minimal public surface; hide implementation details; enable future refactoring.

---

## Final Directory Structure (CORRECTED)

```
ainalyn/
  domain/
    entities/
      __init__.py
      agent_definition.py
      workflow.py
      node.py
      module.py
      prompt.py
      tool.py
    rules/
      __init__.py
      definition_rules.py
    errors.py                    # NEW: Domain errors with corrected naming

  application/
    use_cases/
      __init__.py
      compile_definition.py
      validate_definition.py
      export_definition.py
    ports/                       # MOVED from top-level
      __init__.py
      inbound/
        __init__.py
        compile_agent_definition.py      # ICompileAgentDefinition
        validate_agent_definition.py     # IValidateAgentDefinition
        export_agent_definition.py       # IExportAgentDefinition
      outbound/
        __init__.py
        definition_schema_validation.py  # IDefinitionSchemaValidator
        definition_static_analysis.py    # IDefinitionAnalyzer
        definition_serialization.py      # IDefinitionSerializer
        definition_persistence.py        # IDefinitionWriter
    services.py                  # Updated with DI
    __init__.py

  adapters/
    inbound/                     # RENAMED from primary
      __init__.py
      builders/                  # KEPT HERE (not moved to application)
        __init__.py
        agent_builder.py
        workflow_builder.py
        node_builder.py
        module_builder.py
        prompt_builder.py
        tool_builder.py
    outbound/                    # RENAMED from secondary
      __init__.py
      schema_validator.py        # Implements IDefinitionSchemaValidator
      static_analyzer.py         # Implements IDefinitionAnalyzer
      yaml_serializer.py         # Implements IDefinitionSerializer
      file_writer.py             # Implements IDefinitionWriter

  infrastructure/                # NEW: Wiring layer
    __init__.py
    service_factory.py
    default_config.py

  # Top-level convenience
  __init__.py                    # Minimal public exports
  api.py                         # High-level functions (uses factory)
  cli.py                         # CLI entry point
  _version.py
```

---

## Migration Steps (CORRECTED)

### Step 0: Add Infrastructure Layer
1. Create `infrastructure/` directory
2. Create `infrastructure/service_factory.py`
3. Create `infrastructure/__init__.py`

### Step 1: Create Domain Errors
1. Create `domain/errors.py` with corrected naming
2. Add platform boundary warnings to all docstrings
3. Update domain entities to use new errors

### Step 2: Create Ports Structure
1. Create `application/ports/` directory
2. Create `application/ports/inbound/` and `outbound/`
3. Move and rename port interfaces from `ports/` to `application/ports/`
4. Update port names to use-case + definition naming
5. Add platform warnings to port docstrings

### Step 3: Update Application Layer
1. Update `DefinitionService.__init__` to accept port dependencies
2. Update use cases to use new port interfaces
3. Update use cases to import from `application.ports`

### Step 4: Update Outbound Adapters
1. Rename `adapters/secondary/` → `adapters/outbound/`
2. Rename adapter files:
   - `validators.py` → `schema_validator.py`
   - `analyzers.py` → `static_analyzer.py`
   - `exporters.py` → `yaml_serializer.py`
   - Add `file_writer.py`
3. Update adapters to implement new port interfaces
4. Update all imports

### Step 5: Update Inbound Adapters
1. Rename `adapters/primary/` → `adapters/inbound/`
2. Create `adapters/inbound/builders/` directory
3. Move builder files to `builders/` subdirectory
4. Update builders to:
   - Use domain errors
   - Add platform boundary warnings
   - Delegate validation to domain entities
5. Delete `adapters/inbound/errors.py` (moved to domain)
6. Update all imports

### Step 6: Wire Dependencies
1. Implement `infrastructure/service_factory.py`
2. Update `api.py` to use factory
3. Update `cli.py` to use factory

### Step 7: Update Public API
1. Update `__init__.py` to minimal exports
2. Add platform boundary warning to module docstring
3. Only export user-facing API

### Step 8: Delete Old Structure
1. Delete `ports/` directory (moved to `application/ports/`)
2. Verify no imports reference old locations

### Step 9: Update Tests
1. Update test imports for new structure
2. Update test fixtures to use service factory
3. Add tests for platform boundary warnings
4. Verify all tests pass

### Step 10: Update Documentation
1. Update architecture diagrams
2. Update API documentation
3. Update CONTRIBUTING.md
4. Update README.md
5. Add platform boundaries guide

---

## Constitutional Compliance Checklist

### ✅ Must Satisfy (Hard Requirements)

- [ ] SDK is positioned as Compiler, not Runtime
- [ ] No execution/billing authority in SDK
- [ ] Platform boundary warnings in all appropriate places:
  - [ ] ValidationResult
  - [ ] YAML export header
  - [ ] Builder docstrings
  - [ ] Module docstring
- [ ] Error names don't suggest execution semantics
- [ ] Domain errors separated from adapter concerns
- [ ] Builders classified as inbound adapters (not application)
- [ ] Infrastructure layer handles dependency wiring
- [ ] Public API doesn't leak internal structure
- [ ] Port names emphasize business intent
- [ ] Validation boundaries clearly defined

---

## Benefits of This Refactoring

1. **Constitutional Compliance**: Aligns with all platform rules
2. **Clear Dependency Direction**: Core (domain + application) doesn't depend on adapters
3. **Better Testability**: Easy to mock dependencies via ports
4. **Single Responsibility**: Each layer has clear, non-overlapping responsibilities
5. **Easier to Extend**: New adapters can be added without touching core
6. **Explicit Contracts**: Ports clearly define what core needs
7. **Platform Boundaries**: Explicit warnings prevent developer confusion
8. **Clean Public API**: Minimal exposure enables future refactoring

---

## Risks and Mitigation

### Risk 1: Breaking Changes
**Severity**: Medium
**Mitigation**:
- Keep public API (`api.py`, `__init__.py`) stable
- Internal refactoring only
- Maintain backward compatibility at module exports
- Users importing from `ainalyn` (not submodules) won't break

### Risk 2: Test Failures
**Severity**: High (160+ tests)
**Mitigation**:
- Update tests incrementally (step-by-step)
- Run tests after each migration step
- Use service factory in tests for consistent DI
- Maintain test coverage above 85%

### Risk 3: Import Complexity
**Severity**: Low
**Mitigation**:
- Update `__init__.py` files to re-export at appropriate levels
- Maintain clean public API surface
- Document internal imports for contributors only

### Risk 4: Constitutional Violations
**Severity**: CRITICAL
**Mitigation**:
- This plan explicitly addresses all constitutional requirements
- Platform boundary warnings are mandatory
- Regular review against rule-docs

---

## Success Criteria

- [ ] All tests pass (160+ tests)
- [ ] `mypy --strict` passes with zero errors
- [ ] `ruff check` passes with zero errors
- [ ] No circular dependencies
- [ ] Domain layer has zero adapter imports
- [ ] Application layer depends only on domain + ports
- [ ] Adapters implement port interfaces
- [ ] Public API remains stable (no breaking changes)
- [ ] Platform boundary warnings present in all required locations
- [ ] Error names emphasize compile-time semantics
- [ ] Infrastructure layer properly wires dependencies
- [ ] Documentation updated (architecture, API, guides)

---

## Execution Ready

This plan is now **APPROVED and READY FOR EXECUTION**.

All corrections from `REFACTOR_PLAN_REVIEW.md` have been incorporated:
- ✅ Builders stay as inbound adapters
- ✅ Infrastructure layer added
- ✅ Platform warnings added
- ✅ Error naming corrected
- ✅ Public API reduced
- ✅ Port naming improved
- ✅ Constitutional compliance ensured

**Next**: User indicates how to proceed with execution.
