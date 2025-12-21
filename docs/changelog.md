# Changelog

All notable changes to the Ainalyn SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation with MkDocs
- Getting Started guides (Installation, Quickstart, Your First Agent)
- Core Concepts documentation (Platform Boundaries, Compiler vs Runtime, Architecture, Agent Definition)
- Example projects (basic_agent.py, multi_workflow_agent.py)
- Troubleshooting guide
- API reference documentation structure

### Changed
- Enhanced CONTRIBUTING.md with links to new documentation
- Improved README.md with documentation references

### Fixed
- N/A

## [0.1.0] - 2024-12-22

Initial release of the Ainalyn SDK.

### Added

#### Core Features
- **Builder API**: Fluent builders for all entity types
  - `AgentBuilder` - Build agent definitions
  - `WorkflowBuilder` - Build workflows
  - `NodeBuilder` - Build nodes
  - `ModuleBuilder` - Build modules
  - `PromptBuilder` - Build prompts
  - `ToolBuilder` - Build tools

#### Domain Entities
- `AgentDefinition` - Complete agent specification (aggregate root)
- `Workflow` - Task execution workflow
- `Node` - Individual task unit
- `Module` - Reusable capability component
- `Prompt` - LLM interaction template
- `Tool` - External integration specification

#### Validation
- Comprehensive validation rules
  - Name format validation (valid Python identifiers)
  - Semantic version validation
  - Circular dependency detection
  - Platform boundary compliance checks
- `validate()` API function for agent validation

#### Export
- YAML export functionality
- `export_yaml()` API function
- `compile_agent()` convenience function (validate + export)

#### Architecture
- Clean Hexagonal Architecture implementation
- Five-layer design:
  - Layer 1: Domain (pure business logic)
  - Layer 2: Ports (interface definitions)
  - Layer 3: Adapters (implementations)
  - Layer 4: Application (use cases & services)
  - Layer 5: API & CLI (public interfaces)

#### CLI
- Command-line interface for common operations
- Commands:
  - `ainalyn validate <file>` - Validate agent definition
  - `ainalyn compile <file>` - Compile to YAML
  - `ainalyn version` - Show SDK version
  - `ainalyn --help` - Show help

#### Type Safety
- Full type hints throughout codebase
- MyPy strict mode compliance
- Protocol-based interfaces for flexibility

#### Testing
- Comprehensive test suite
  - Unit tests for all components
  - Integration tests for end-to-end flows
- >85% code coverage
- Separate unit and integration test directories

#### Development Tools
- Pre-commit hooks for code quality
- Ruff for linting and formatting
- MyPy for type checking
- Pytest for testing
- Coverage for test coverage reporting

#### Documentation
- Comprehensive README.md
- Detailed CONTRIBUTING.md
- Test documentation (tests/README.md)
- Platform boundary specifications (ref-boundary/)
  - Platform Vision & System Boundary
  - Agent Definition Compiler & Runtime Forbidden Zone
  - Agent Canonical Definition
  - Execution Lifecycle & Authority
  - Execution Billing, Pricing & Revenue Boundary
  - Official Client Execution Presentation Contract

#### Platform Boundary Enforcement
- No execution semantics
- No platform authority
- No billing/pricing logic
- No autonomous agent patterns
- Clear separation of concerns (compiler vs runtime)

### Dependencies
- **Runtime**: PyYAML >=6.0 (only runtime dependency)
- **Development**: pytest, mypy, ruff, coverage, pre-commit
- **Documentation**: mkdocs, mkdocs-material, mkdocstrings[python]

### Platform Support
- Python 3.11, 3.12, 3.13
- Cross-platform (Windows, macOS, Linux)

---

## Version History

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** (x.0.0): Incompatible API changes
- **MINOR** (0.x.0): New features (backward compatible)
- **PATCH** (0.0.x): Bug fixes (backward compatible)

### Release Process

1. Update CHANGELOG.md with changes
2. Update version in pyproject.toml
3. Create git tag (`git tag v0.1.0`)
4. Push tag (`git push origin v0.1.0`)
5. GitHub Actions builds and publishes to PyPI
6. Update documentation

### Migration Guides

#### Upgrading to 0.1.0

Initial release - no migration needed.

---

## Links

- [GitHub Repository](https://github.com/ainalyn/ainalyn-sdk)
- [PyPI Package](https://pypi.org/project/ainalyn-sdk/)
- [Documentation](https://docs.ainalyn.io/sdk)
- [Issue Tracker](https://github.com/ainalyn/ainalyn-sdk/issues)
- [Discussions](https://github.com/ainalyn/ainalyn-sdk/discussions)

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details on:
- How to contribute
- Code standards
- Testing requirements
- Pull request process

---

**Format**: This changelog follows the [Keep a Changelog](https://keepachangelog.com/) format.

**Categories**:
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
