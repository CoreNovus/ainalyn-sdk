# Contributing to Ainalyn SDK

Thank you for your interest in contributing to the Ainalyn SDK! We're excited to have you join our community.

This guide will help you understand our development process, coding standards, and how to make effective contributions.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Architecture & Design Principles](#architecture--design-principles)
- [Platform Boundaries (CRITICAL)](#platform-boundaries-critical)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)
- [Community & Support](#community--support)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Getting Started

### Prerequisites

- **Python 3.11+** (we support 3.11, 3.12, and 3.13)
- **Git** for version control
- Basic understanding of Python packaging and type hints
- Familiarity with dataclasses and immutable design patterns

### Setting Up Development Environment

1. **Fork and Clone the Repository**

   ```bash
   # Fork the repository on GitHub first, then:
   git clone https://github.com/YOUR_USERNAME/ainalyn-sdk.git
   cd ainalyn-sdk
   ```

2. **Create a Virtual Environment**

   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Development Dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

   This installs the SDK in editable mode along with all development tools:
   - pytest (testing)
   - mypy (type checking)
   - ruff (linting and formatting)
   - coverage (code coverage)
   - pre-commit (git hooks)

4. **Set Up Pre-commit Hooks**

   ```bash
   pre-commit install
   ```

   This ensures code quality checks run automatically before each commit.

5. **Verify Installation**

   ```bash
   # Run tests
   pytest

   # Run type checker
   mypy ainalyn/

   # Run linter
   ruff check ainalyn/
   ```

---

## Development Workflow

### Branch Naming

Use descriptive branch names following this pattern:

- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/documentation-update` - Documentation changes
- `refactor/component-name` - Code refactoring
- `test/test-description` - Test improvements

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```text
feat(builders): add support for conditional workflows

fix(validators): correct validation for nested modules

docs(readme): update installation instructions

test(analyzers): add edge case tests for circular dependency detection
```

---

## Architecture & Design Principles

The Ainalyn SDK follows **Clean Hexagonal Architecture** with strict adherence to **SOLID principles**.

For detailed architecture documentation, see:

- **[Architecture Overview](docs/concepts/architecture-overview.md)** - High-level architecture explanation
- **[Hexagonal Architecture](docs/contributor-guide/architecture/hexagonal-architecture.md)** - Detailed architecture guide
- **[Layer Documentation](docs/contributor-guide/architecture/)** - Layer-by-layer deep dives

### Architecture Layers

```text
ainalyn/
├── domain/              # Business logic and entities
│   ├── entities/        # Core domain models (immutable dataclasses)
│   ├── rules/           # Domain rules and validation logic
│   └── errors.py        # Domain-level exceptions
├── application/         # Application layer
│   ├── ports/           # Interface definitions
│   │   ├── inbound/     # Primary ports (use case interfaces)
│   │   └── outbound/    # Secondary ports (infrastructure interfaces)
│   ├── use_cases/       # Application use cases
│   └── services.py      # High-level application services
├── adapters/            # Implementations of ports
│   ├── inbound/         # Primary adapters (Builder API)
│   │   └── builders/
│   └── outbound/        # Secondary adapters (Validators, Exporters)
├── infrastructure/      # Infrastructure setup
│   └── service_factory.py
└── runtime/             # Optional runtime wrapper
    └── decorators.py
```

### Design Principles

1. **Immutability**: All domain entities MUST be frozen dataclasses
2. **Single Responsibility**: Each class has one reason to change
3. **Dependency Inversion**: Depend on abstractions (Protocols), not concretions
4. **Interface Segregation**: Small, focused interfaces
5. **Open/Closed**: Open for extension, closed for modification

### Example: Adding a New Entity

```python
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class NewEntity:
    """
    Brief description of the entity.

    This entity represents... (explanation)

    Attributes:
        name: Entity name following platform naming conventions.
        description: Human-readable description.
    """
    name: str
    description: str

    def __post_init__(self) -> None:
        """Validate entity constraints after initialization."""
        if not self.name:
            raise ValueError("name cannot be empty")
```

---

## Platform Boundaries (CRITICAL)

> ⚠️ **CRITICAL**: The Ainalyn SDK is a **compiler, not a runtime**. Violating these boundaries will result in PR rejection.

### Forbidden Concepts

The SDK **MUST NOT** contain any of the following:

#### ❌ Execution Semantics

- No `execute()`, `run()`, `start()` methods on entities
- No execution lifecycle management
- No state machines for execution states
- No `executionId` concept anywhere

#### ❌ Billing/Pricing Logic

- No price calculation
- No cost estimation
- No billing logic
- No usage metering as source of truth

#### ❌ Platform Authority

- No retry/timeout/fallback execution decisions
- No determination of success/failure
- No generation of platform facts (executionId, execution status)

#### ❌ Autonomous Agent Patterns

- No autonomous loops
- No self-planning systems
- No reflection or memory-driven continuous behavior

### Required Disclaimers

Any new public-facing documentation or docstrings MUST include appropriate disclaimers:

```python
"""
This SDK is a compiler, not a runtime. It produces descriptions
that are submitted to the Ainalyn Platform for execution. The SDK
does not execute Agents or make any decisions about execution,
billing, or pricing.
"""
```

### Boundary Verification

Before submitting a PR, verify compliance:

```bash
# Search for forbidden concepts
grep -r "executionId\|autonomous\|retry.*logic\|billing.*calc" ainalyn/

# Should return no results in implementation code
```

For detailed boundary rules, see:

- `ref-boundary/Platform Vision & System Boundary.md`
- `ref-boundary/Agent Definition Compiler & Runtime Forbidden Zone.md`
- `COMPLIANCE_REPORT.md`

---

## Coding Standards

### Type Annotations

- **Always** use type hints for function signatures and class attributes
- Use `from __future__ import annotations` at the top of every file
- Avoid `Any` types - be explicit
- Use Protocol for interface definitions

```python
from __future__ import annotations

from typing import Protocol

class Validator(Protocol):
    """Interface for validators."""

    def validate_schema(self, definition: AgentDefinition) -> list[ValidationError]:
        """Validate an agent definition."""
        ...
```

### Imports

- Use absolute imports: `from ainalyn.domain.entities import AgentDefinition`
- Group imports: standard library, third-party, local
- Use `TYPE_CHECKING` for type-only imports to avoid circular dependencies

```python
from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from ainalyn.domain.entities import AgentDefinition

if TYPE_CHECKING:
    from ainalyn.ports.inbound.validator import ValidationResult
```

### Docstrings

Use Google-style docstrings for all public APIs:

```python
def validate(definition: AgentDefinition) -> ValidationResult:
    """
    Validate an AgentDefinition.

    This function performs comprehensive validation including schema
    validation and static analysis.

    Args:
        definition: The AgentDefinition to validate.

    Returns:
        ValidationResult containing all errors and warnings found.
        Use result.is_valid to check if validation passed.

    Example:
        >>> from ainalyn import AgentBuilder, validate
        >>> agent = AgentBuilder("my-agent").version("1.0.0").build()
        >>> result = validate(agent)
        >>> if result.is_valid:
        ...     print("Valid!")
    """
```

### Code Style

We use **Ruff** for linting and formatting:

```bash
# Check code
ruff check ainalyn/ tests/

# Auto-fix issues
ruff check --fix ainalyn/ tests/

# Format code
ruff format ainalyn/ tests/
```

Configuration is in `pyproject.toml`. Key rules:

- Line length: 88 characters
- Use double quotes for strings
- Mandatory `from __future__ import annotations`

---

## Testing Guidelines

### Test Structure

Tests must mirror the source code structure:

```text
tests/
├── unit/              # Unit tests
│   ├── domain/
│   │   ├── entities/
│   │   └── rules/
│   ├── adapters/
│   │   ├── primary/
│   │   └── secondary/
│   └── application/
└── integration/       # Integration tests
```

### Writing Tests

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- Use pytest fixtures for reusable test data
- Aim for >85% code coverage

```python
from __future__ import annotations

import pytest

from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder, ModuleBuilder

@pytest.fixture
def sample_module():
    """Provide a sample Module for testing."""
    return ModuleBuilder("test-module").description("Test module").build()

def test_agent_builder_requires_workflow(sample_module):
    """Test that AgentBuilder requires at least one workflow."""
    with pytest.raises(EmptyCollectionError, match="workflows"):
        (
            AgentBuilder("test-agent")
            .version("1.0.0")
            .description("Test")
            .add_module(sample_module)
            .build()
        )
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ainalyn --cov-report=term-missing

# Run specific test file
pytest tests/unit/adapters/primary/test_builders.py

# Run tests matching a pattern
pytest -k "test_builder"
```

### Test Requirements

- All new features MUST include tests
- All bug fixes MUST include regression tests
- Maintain or improve code coverage
- Tests must pass mypy strict mode
- Tests must pass all ruff checks

---

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**

   ```bash
   pytest
   ```

2. **Run type checker**

   ```bash
   mypy ainalyn/
   ```

3. **Run linter**

   ```bash
   ruff check ainalyn/ tests/
   ```

4. **Check coverage**

   ```bash
   pytest --cov=ainalyn --cov-report=term-missing
   ```

5. **Verify boundary compliance**

   ```bash
   # Should return no results in implementation code
   grep -r "executionId\|autonomous.*agent\|retry.*execution" ainalyn/
   ```

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Boundary Compliance
- [ ] No execution semantics added
- [ ] No billing/pricing logic added
- [ ] No platform authority claimed
- [ ] Appropriate disclaimers added if needed

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated (if applicable)
- [ ] All tests pass
- [ ] Code coverage maintained/improved

## Code Quality
- [ ] mypy strict mode passes
- [ ] ruff checks pass
- [ ] Documentation updated (if applicable)

## Related Issues
Closes #<issue_number>
```

### Review Process

1. **Automated Checks**: CI/CD runs tests, type checks, and linting
2. **Boundary Review**: Maintainers verify platform boundary compliance
3. **Code Review**: At least one maintainer reviews the code
4. **Documentation Review**: Check for clarity and completeness
5. **Merge**: After approval and passing checks

### PR Guidelines

- Keep PRs focused on a single concern
- Provide clear descriptions and context
- Reference related issues
- Respond to review feedback promptly
- Ensure commit history is clean (squash if needed)

---

## Documentation

### Documentation Resources

The Ainalyn SDK has comprehensive documentation. When contributing, you may need to reference or update:

- **[Complete Documentation](docs/index.md)** - Full documentation site
- **[Getting Started](docs/getting-started/installation.md)** - Installation and quickstart guides
- **[Core Concepts](docs/concepts/platform-boundaries.md)** - Understanding SDK boundaries and architecture
- **[User Guide](docs/user-guide/building-agents/using-builder-api.md)** - Detailed usage guides
- **[API Reference](docs/api-reference/builders/agent-builder.md)** - Complete API documentation
- **[Contributor Guide](docs/contributor-guide/development-setup.md)** - Development and architecture guides
- **[Examples](examples/)** - Runnable example code
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Changelog](docs/changelog.md)** - Version history

### What Needs Documentation

- All public APIs (functions, classes, methods)
- All modules and packages (`__init__.py` docstrings)
- README updates for new features
- Architecture decisions (in code comments or ADR)
- User-facing documentation in `docs/` for significant features

### Documentation Style

- Use clear, concise language
- Provide examples for complex features
- Include type information in docstrings
- Explain the "why", not just the "what"

### Example Documentation

```python
class AgentBuilder:
    """
    Fluent builder for constructing AgentDefinition entities.

    This builder provides a chainable API for creating valid AgentDefinitions
    with compile-time type safety and runtime validation. The builder pattern
    ensures that only valid Agent Definitions can be constructed.

    Important:
        AgentDefinition is a pure description entity with no execution
        semantics. The SDK compiles definitions for platform submission.

    Example:
        >>> builder = AgentBuilder("my-agent")
        >>> agent = (
        ...     builder
        ...     .version("1.0.0")
        ...     .description("My first agent")
        ...     .add_workflow(workflow)
        ...     .build()
        ... )

    See Also:
        - WorkflowBuilder: For building workflows
        - NodeBuilder: For building nodes
    """
```

---

## Community & Support

### Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Discord**: Join our [Discord community](https://discord.gg/ainalyn)
- **Email**: <dev@ainalyn.io>

### Reporting Issues

When reporting bugs, include:

1. **Environment**: Python version, OS, SDK version
2. **Steps to Reproduce**: Minimal code example
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Error Messages**: Full stack traces

### Feature Requests

For new features:

1. Check existing issues to avoid duplicates
2. Provide clear use case and motivation
3. Consider platform boundaries - features must not violate SDK scope
4. Be prepared to discuss implementation approach

### Asking Questions

- Use GitHub Discussions for "how-to" questions
- Search existing issues and discussions first
- Provide context and code examples
- Be respectful and patient

---

## Development Best Practices

### 1. Start Small

If you're new to the project:

- Start with documentation improvements
- Fix typos or clarify existing docs
- Add missing docstrings
- Improve test coverage
- Then move to bug fixes and features

### 2. Communicate Early

- Comment on issues you want to work on
- Discuss design approaches before large changes
- Ask questions if anything is unclear
- Share progress on complex features

### 3. Maintain Quality

- Write tests first (TDD)
- Keep functions small and focused
- Avoid premature optimization
- Refactor incrementally
- Document as you go

### 4. Respect Boundaries

- Always keep SDK scope in mind
- Review `ref-boundary/` documents
- Question features that feel like execution logic
- Maintain architectural integrity

---

## Release Process

> Note: Only maintainers can create releases

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

---

## Recognition

We value all contributions! Contributors will be:

- Listed in release notes
- Credited in the repository
- Recognized in the community

---

## Quick Reference

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install -e ".[dev]"
pre-commit install

# Development
pytest                        # Run tests
mypy ainalyn/                # Type check
ruff check ainalyn/ tests/   # Lint
ruff format ainalyn/ tests/  # Format

# Before PR
pytest --cov=ainalyn --cov-report=term-missing
mypy ainalyn/
ruff check ainalyn/ tests/
grep -r "executionId\|autonomous" ainalyn/  # Boundary check
```

---

## Thank You

Your contributions make Ainalyn SDK better for everyone. We appreciate your time and effort! 🎉

If you have questions about this guide, please open an issue or discussion.

Happy coding! 🚀
