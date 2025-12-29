"""
Use case for compiling Agent Definitions.

This module implements the compilation use case that orchestrates
validation and export in a unified workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.application.use_cases.export_definition import ExportDefinitionUseCase
    from ainalyn.application.use_cases.validate_definition import (
        ValidateDefinitionUseCase,
    )
    from ainalyn.domain.entities import AgentDefinition
    from ainalyn.application.ports.inbound.validate_agent_definition import (
        ValidationResult,
    )


@dataclass(frozen=True, slots=True)
class CompilationResult:
    """
    Result of a compilation operation.

    This immutable data class contains the validation result
    and optionally the exported YAML content.

    Attributes:
        validation_result: The result of validation.
        yaml_content: The exported YAML string if validation passed,
            None otherwise.
        output_path: The file path where YAML was written, if applicable.

    Example:
        >>> result = CompilationResult(
        ...     validation_result=validation_result,
        ...     yaml_content=yaml_string,
        ...     output_path=Path("agent.yaml"),
        ... )
        >>> if result.is_successful:
        ...     print(f"Compiled to {result.output_path}")
    """

    validation_result: ValidationResult
    yaml_content: str | None = None
    output_path: Path | None = None

    @property
    def is_successful(self) -> bool:
        """
        Check if compilation was successful.

        Returns:
            bool: True if validation passed and YAML was exported,
                False otherwise.
        """
        return self.validation_result.is_valid and self.yaml_content is not None


class CompileDefinitionUseCase:
    """
    Use case for compiling Agent Definitions.

    This use case orchestrates the complete compilation workflow:
    1. Validate the AgentDefinition (schema + static analysis)
    2. Export to YAML (only if validation passes)
    3. Optionally write to file

    The use case ensures that invalid definitions are never exported,
    maintaining the integrity of the compilation process.

    Example:
        >>> from ainalyn.adapters.secondary import (
        ...     SchemaValidator, StaticAnalyzer, YamlExporter
        ... )
        >>> from ainalyn.application.use_cases import (
        ...     ValidateDefinitionUseCase,
        ...     ExportDefinitionUseCase,
        ...     CompileDefinitionUseCase,
        ... )
        >>> validator = ValidateDefinitionUseCase(
        ...     SchemaValidator(), StaticAnalyzer()
        ... )
        >>> exporter = ExportDefinitionUseCase(YamlExporter())
        >>> compiler = CompileDefinitionUseCase(validator, exporter)
        >>> result = compiler.execute(agent_definition)
        >>> if result.is_successful:
        ...     print("Compilation successful!")
        ...     print(result.yaml_content)
    """

    def __init__(
        self,
        validate_use_case: ValidateDefinitionUseCase,
        export_use_case: ExportDefinitionUseCase,
    ) -> None:
        """
        Initialize the compilation use case.

        Args:
            validate_use_case: The validation use case.
            export_use_case: The export use case.
        """
        self._validate_use_case = validate_use_case
        self._export_use_case = export_use_case

    def execute(self, definition: AgentDefinition) -> CompilationResult:
        """
        Compile an AgentDefinition.

        This method performs validation and, if successful, exports
        the definition to YAML format.

        Args:
            definition: The AgentDefinition to compile.

        Returns:
            CompilationResult: Contains validation result and YAML content
                (if validation passed).

        Note:
            YAML export only occurs if validation produces no ERROR-level
            issues. Warnings do not prevent export.
        """
        # Phase 1: Validation
        validation_result = self._validate_use_case.execute(definition)

        # Phase 2: Export (only if validation passed)
        yaml_content = None
        if validation_result.is_valid:
            yaml_content = self._export_use_case.execute(definition)

        return CompilationResult(
            validation_result=validation_result,
            yaml_content=yaml_content,
        )

    def execute_to_file(
        self,
        definition: AgentDefinition,
        output_path: Path,
    ) -> CompilationResult:
        """
        Compile an AgentDefinition and write to file.

        This method performs validation and, if successful, exports
        the definition to a YAML file.

        Args:
            definition: The AgentDefinition to compile.
            output_path: The destination file path.

        Returns:
            CompilationResult: Contains validation result, YAML content,
                and output path (if validation passed).

        Raises:
            IOError: If the file cannot be written.
            PermissionError: If write permission is denied.

        Note:
            The file is only written if validation produces no ERROR-level
            issues. Warnings do not prevent file creation.
        """
        # Phase 1: Validation
        validation_result = self._validate_use_case.execute(definition)

        # Phase 2: Export to file (only if validation passed)
        yaml_content = None
        file_path = None
        if validation_result.is_valid:
            self._export_use_case.execute_to_file(definition, output_path)
            yaml_content = self._export_use_case.execute(definition)
            file_path = output_path

        return CompilationResult(
            validation_result=validation_result,
            yaml_content=yaml_content,
            output_path=file_path,
        )
