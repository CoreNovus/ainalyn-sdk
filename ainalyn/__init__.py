"""
Ainalyn SDK - Agent Definition Compiler.

A Python SDK for describing, validating, and exporting Agent Definitions
for the Ainalyn Task-Oriented Agent Marketplace Platform.

This SDK provides tools for developers to:
- Define Agents using a fluent builder API or decorators
- Validate Agent Definitions against platform requirements
- Export definitions to YAML format for platform submission

Important: This SDK is a compiler, not a runtime. It produces descriptions
that are submitted to the Ainalyn Platform for execution. The SDK does not
execute Agents or make any decisions about execution, billing, or pricing.

Example:
    >>> from ainalyn import AgentBuilder, workflow, node
    >>> agent = (
    ...     AgentBuilder("my-agent")
    ...     .version("1.0.0")
    ...     .description("My first agent")
    ...     .build()
    ... )

For more information, see the documentation at https://docs.ainalyn.io/sdk
"""

from __future__ import annotations

from ainalyn._version import __version__
from ainalyn.adapters.inbound import (
    AgentBuilder,
    BuilderError,
    DuplicateNameError,
    EmptyCollectionError,
    InvalidReferenceError,
    InvalidValueError,
    MissingRequiredFieldError,
    ModuleBuilder,
    NodeBuilder,
    PromptBuilder,
    ToolBuilder,
    WorkflowBuilder,
)
from ainalyn.adapters.outbound import SchemaValidator, StaticAnalyzer, YamlExporter
from ainalyn.api import compile_agent, export_yaml, validate
from ainalyn.application import (
    CompilationResult,
    CompileDefinitionUseCase,
    DefinitionService,
    ExportDefinitionUseCase,
    ValidateDefinitionUseCase,
)
from ainalyn.domain.entities import (
    AgentDefinition,
    Module,
    Node,
    NodeType,
    Prompt,
    Tool,
    Workflow,
)
from ainalyn.application.ports.inbound.validate_agent_definition import (
    Severity,
    ValidationError,
    ValidationResult,
)
from ainalyn.domain.rules import DefinitionRules

__all__ = [
    # High-level API Functions
    "validate",
    "export_yaml",
    "compile_agent",
    # Domain Entities
    "AgentDefinition",
    "Module",
    "Node",
    "NodeType",
    "Prompt",
    "Tool",
    "Workflow",
    # Domain Rules
    "DefinitionRules",
    # Builders (Primary Adapters)
    "AgentBuilder",
    "ModuleBuilder",
    "NodeBuilder",
    "PromptBuilder",
    "ToolBuilder",
    "WorkflowBuilder",
    # Builder Errors
    "BuilderError",
    "DuplicateNameError",
    "EmptyCollectionError",
    "InvalidReferenceError",
    "InvalidValueError",
    "MissingRequiredFieldError",
    # Secondary Adapters
    "SchemaValidator",
    "StaticAnalyzer",
    "YamlExporter",
    # Application Services
    "DefinitionService",
    # Application Use Cases
    "ValidateDefinitionUseCase",
    "ExportDefinitionUseCase",
    "CompileDefinitionUseCase",
    # Results
    "CompilationResult",
    # Validation
    "Severity",
    "ValidationError",
    "ValidationResult",
    # Version
    "__version__",
]
