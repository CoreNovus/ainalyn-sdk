"""
Application services for Ainalyn SDK.

This module provides high-level services that encapsulate
use cases and provide a simplified API for SDK consumers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.adapters.secondary.analyzers import StaticAnalyzer
from ainalyn.adapters.secondary.exporters import YamlExporter
from ainalyn.adapters.secondary.validators import SchemaValidator
from ainalyn.application.use_cases.compile_definition import (
    CompilationResult,
    CompileDefinitionUseCase,
)
from ainalyn.application.use_cases.export_definition import ExportDefinitionUseCase
from ainalyn.application.use_cases.validate_definition import ValidateDefinitionUseCase

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.domain.entities import AgentDefinition
    from ainalyn.ports.inbound.validator import ValidationResult


class DefinitionService:
    """
    Unified service for Agent Definition operations.

    This service provides a simplified, high-level API for working with
    Agent Definitions. It encapsulates all use cases and manages their
    dependencies, offering a clean interface for SDK consumers.

    The service supports three main operations:
    1. Validation - Verify structural and logical correctness
    2. Export - Convert to YAML format
    3. Compilation - Complete validate-and-export workflow

    Example:
        >>> from ainalyn.application.services import DefinitionService
        >>> from pathlib import Path
        >>> service = DefinitionService()
        >>> # Validate only
        >>> result = service.validate(agent_definition)
        >>> if result.is_valid:
        ...     print("Valid!")
        >>> # Compile to string
        >>> compilation = service.compile(agent_definition)
        >>> if compilation.is_successful:
        ...     print(compilation.yaml_content)
        >>> # Compile to file
        >>> compilation = service.compile_to_file(
        ...     agent_definition,
        ...     Path("agent.yaml")
        ... )
    """

    def __init__(self) -> None:
        """
        Initialize the definition service.

        This constructor sets up all necessary adapters and use cases
        with their proper dependencies.
        """
        # Initialize secondary adapters
        self._schema_validator = SchemaValidator()
        self._static_analyzer = StaticAnalyzer()
        self._yaml_exporter = YamlExporter()

        # Initialize use cases
        self._validate_use_case = ValidateDefinitionUseCase(
            self._schema_validator,
            self._static_analyzer,
        )
        self._export_use_case = ExportDefinitionUseCase(self._yaml_exporter)
        self._compile_use_case = CompileDefinitionUseCase(
            self._validate_use_case,
            self._export_use_case,
        )

    def validate(self, definition: AgentDefinition) -> ValidationResult:
        """
        Validate an AgentDefinition.

        This method performs comprehensive validation including:
        - Schema validation (structural correctness)
        - Static analysis (logical consistency)

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            ValidationResult: Contains all errors and warnings found.
                Use result.is_valid to check if validation passed.

        Example:
            >>> service = DefinitionService()
            >>> result = service.validate(agent_definition)
            >>> if not result.is_valid:
            ...     for error in result.errors:
            ...         print(f"{error.code}: {error.message}")
        """
        return self._validate_use_case.execute(definition)

    def export(self, definition: AgentDefinition) -> str:
        """
        Export an AgentDefinition to YAML string.

        This method converts the AgentDefinition into a YAML-formatted
        string without performing validation. For safety, use compile()
        instead to ensure validation before export.

        Args:
            definition: The AgentDefinition to export.

        Returns:
            str: The YAML-formatted string representation.

        Raises:
            yaml.YAMLError: If YAML serialization fails.

        Warning:
            This method does not validate the definition before export.
            Use compile() for a safer, validated export workflow.

        Example:
            >>> service = DefinitionService()
            >>> yaml_string = service.export(agent_definition)
            >>> print(yaml_string)
        """
        return self._export_use_case.execute(definition)

    def export_to_file(self, definition: AgentDefinition, path: Path) -> None:
        """
        Export an AgentDefinition to a YAML file.

        This method converts the AgentDefinition to YAML and writes it
        to the specified file path without performing validation.
        For safety, use compile_to_file() instead.

        Args:
            definition: The AgentDefinition to export.
            path: The destination file path.

        Raises:
            yaml.YAMLError: If YAML serialization fails.
            IOError: If the file cannot be written.
            PermissionError: If write permission is denied.

        Warning:
            This method does not validate the definition before export.
            Use compile_to_file() for a safer, validated export workflow.

        Example:
            >>> service = DefinitionService()
            >>> service.export_to_file(agent_definition, Path("agent.yaml"))
        """
        self._export_use_case.execute_to_file(definition, path)

    def compile(self, definition: AgentDefinition) -> CompilationResult:
        """
        Compile an AgentDefinition.

        This method performs the complete compilation workflow:
        1. Validate the definition (schema + static analysis)
        2. Export to YAML (only if validation passes)

        Args:
            definition: The AgentDefinition to compile.

        Returns:
            CompilationResult: Contains validation result and YAML content
                (if validation passed).

        Example:
            >>> service = DefinitionService()
            >>> result = service.compile(agent_definition)
            >>> if result.is_successful:
            ...     print("Compilation successful!")
            ...     print(result.yaml_content)
            ... else:
            ...     print("Validation failed:")
            ...     for error in result.validation_result.errors:
            ...         print(f"  {error.code}: {error.message}")
        """
        return self._compile_use_case.execute(definition)

    def compile_to_file(
        self,
        definition: AgentDefinition,
        output_path: Path,
    ) -> CompilationResult:
        """
        Compile an AgentDefinition and write to file.

        This method performs the complete compilation workflow:
        1. Validate the definition (schema + static analysis)
        2. Export to YAML file (only if validation passes)

        Args:
            definition: The AgentDefinition to compile.
            output_path: The destination file path.

        Returns:
            CompilationResult: Contains validation result, YAML content,
                and output path (if validation passed).

        Raises:
            IOError: If the file cannot be written (only if validation passes).
            PermissionError: If write permission is denied (only if validation passes).

        Example:
            >>> service = DefinitionService()
            >>> result = service.compile_to_file(
            ...     agent_definition,
            ...     Path("agent.yaml")
            ... )
            >>> if result.is_successful:
            ...     print(f"Compiled to {result.output_path}")
            ... else:
            ...     print("Validation failed")
        """
        return self._compile_use_case.execute_to_file(definition, output_path)
