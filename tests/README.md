# Ainalyn SDK Tests

This directory contains all tests for the Ainalyn SDK, organized following best practices and mirroring the main codebase structure.

## Directory Structure

```
tests/
├── unit/                      # Unit tests (isolated, fast)
│   ├── domain/               # Domain layer tests
│   │   ├── entities/        # Entity tests
│   │   └── rules/           # Domain rules tests
│   ├── adapters/            # Adapter tests
│   │   └── primary/         # Primary adapter tests
│   └── ports/               # Port interface tests
├── integration/              # Integration tests (cross-layer)
└── README.md                # This file
```

## Test Organization Principles

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Characteristics**:
  - Fast execution (< 1 second each)
  - No external dependencies
  - Mock/stub dependencies
  - Test single responsibility
- **Naming**: `test_<module_name>.py`
- **Structure**: Mirrors main codebase structure

### Integration Tests (`tests/integration/`)
- **Purpose**: Test interaction between components
- **Characteristics**:
  - Test multiple layers together
  - May use real dependencies
  - Slower than unit tests
  - Test end-to-end workflows
- **Naming**: `test_<feature>_integration.py`

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Only Unit Tests
```bash
pytest tests/unit
```

### Run Only Integration Tests
```bash
pytest tests/integration
```

### Run Specific Test File
```bash
pytest tests/unit/domain/entities/test_entities.py
```

### Run Specific Test Class
```bash
pytest tests/unit/domain/entities/test_entities.py::TestModule
```

### Run Specific Test Method
```bash
pytest tests/unit/domain/entities/test_entities.py::TestModule::test_create_module
```

### Run with Coverage
```bash
pytest --cov=ainalyn --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Coverage Requirements

- **Overall**: ≥ 85%
- **Domain Layer**: ≥ 90%
- **Adapters**: ≥ 85%
- **Ports**: ≥ 80%

## Writing Tests

### Test Structure
Each test file should follow this structure:

```python
"""Unit tests for <module_name>."""

from __future__ import annotations

import pytest

from ainalyn.domain.entities import Module


class TestModule:
    """Tests for Module entity."""

    def test_create_module(self) -> None:
        """Test creating a Module entity."""
        module = Module(name="test", description="Test module")

        assert module.name == "test"
        assert module.description == "Test module"
```

### Test Naming Conventions
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_is_being_tested>`
- Use descriptive docstrings

### Test Categories (Markers)
- `@pytest.mark.unit`: Unit tests (default for `tests/unit/`)
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow tests (> 1 second)
- `@pytest.mark.e2e`: End-to-end tests

## Test Maintenance

### Aligning with Code Structure
- When adding a new module in `ainalyn/`, add corresponding test file in `tests/unit/`
- Maintain 1:1 mapping between code modules and test files
- Keep test structure synchronized with code structure

### Best Practices
1. **One Test, One Assertion** (when possible)
2. **Arrange-Act-Assert (AAA)** pattern
3. **Test behavior, not implementation**
4. **Use descriptive test names**
5. **Keep tests independent**
6. **Mock external dependencies**
7. **Clean up test data**

## Current Test Coverage

### Domain Layer
- ✅ **entities**: Complete coverage
  - Module, Prompt, Tool, Node, Workflow, AgentDefinition
- ✅ **rules**: Complete coverage
  - Name validation, version validation, workflow rules, circular dependencies, etc.

### Adapters Layer
- ✅ **primary/errors**: Complete coverage
  - All builder errors
- ✅ **primary/builders**: Complete coverage
  - ModuleBuilder, PromptBuilder, ToolBuilder, NodeBuilder, WorkflowBuilder, AgentBuilder

### Ports Layer
- ⏳ **inbound**: Pending (interfaces only, no logic to test)
- ⏳ **outbound**: Pending (interfaces only, no logic to test)

### Application Layer
- ⏳ **use_cases**: Not yet implemented

## Future Improvements
- [ ] Add integration tests for end-to-end workflows
- [ ] Add property-based testing with Hypothesis
- [ ] Add mutation testing with mutmut
- [ ] Add performance benchmarks
