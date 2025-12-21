"""
High-level API functions for Ainalyn SDK.

This module provides convenient wrapper functions around the
DefinitionService, offering a simplified API for common operations.

These functions are designed for ease of use and quick integration,
abstracting away the service initialization details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.application.services import DefinitionService

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.application.use_cases.compile_definition import CompilationResult
    from ainalyn.domain.entities import AgentDefinition
    from ainalyn.ports.inbound.validator import ValidationResult


# Module-level service instance (singleton pattern)
_service: DefinitionService | None = None


def _get_service() -> DefinitionService:
    """Get or create the module-level DefinitionService instance."""
    global _service
    if _service is None:
        _service = DefinitionService()
    return _service


def validate(definition: AgentDefinition) -> ValidationResult:
    """
    Validate an AgentDefinition.

    This function performs comprehensive validation including:
    - Schema validation (structural correctness)
    - Static analysis (logical consistency)

    Args:
        definition: The AgentDefinition to validate.

    Returns:
        ValidationResult: Contains all errors and warnings found.
            Use result.is_valid to check if validation passed.

    Example:
        >>> from ainalyn import AgentBuilder, validate
        >>> agent = AgentBuilder("my-agent").version("1.0.0").description("Test").build()
        >>> result = validate(agent)
        >>> if result.is_valid:
        ...     print("Validation passed!")
        ... else:
        ...     for error in result.errors:
        ...         print(f"{error.code}: {error.message}")
    """
    service = _get_service()
    return service.validate(definition)


def export_yaml(definition: AgentDefinition) -> str:
    """
    Export an AgentDefinition to YAML string.

    This function converts the AgentDefinition into a YAML-formatted
    string representation without performing validation. For a safer
    workflow that includes validation, use compile_agent() instead.

    Args:
        definition: The AgentDefinition to export.

    Returns:
        str: The YAML-formatted string representation.

    Warning:
        This function does not validate the definition before export.
        Use compile_agent() for a complete validate-and-export workflow.

    Example:
        >>> from ainalyn import AgentBuilder, export_yaml
        >>> agent = AgentBuilder("my-agent").version("1.0.0").description("Test").build()
        >>> yaml_string = export_yaml(agent)
        >>> print(yaml_string)
    """
    service = _get_service()
    return service.export(definition)


def compile_agent(
    definition: AgentDefinition,
    output_path: Path | None = None,
) -> CompilationResult:
    """
    Compile an AgentDefinition with validation and export.

    This function performs the complete compilation workflow:
    1. Validate the definition (schema + static analysis)
    2. Export to YAML (only if validation passes)
    3. Optionally write to file

    Args:
        definition: The AgentDefinition to compile.
        output_path: Optional file path to write the YAML output.
            If None, only returns the YAML string without writing.

    Returns:
        CompilationResult: Contains validation result, YAML content,
            and output path (if file was written).

    Example:
        >>> from ainalyn import AgentBuilder, compile_agent
        >>> from pathlib import Path
        >>> agent = AgentBuilder("my-agent").version("1.0.0").description("Test").build()
        >>> # Compile to string
        >>> result = compile_agent(agent)
        >>> if result.is_successful:
        ...     print(result.yaml_content)
        >>> # Compile to file
        >>> result = compile_agent(agent, Path("agent.yaml"))
        >>> if result.is_successful:
        ...     print(f"Compiled to {result.output_path}")
        ... else:
        ...     for error in result.validation_result.errors:
        ...         print(f"{error.code}: {error.message}")
    """
    service = _get_service()
    if output_path is not None:
        return service.compile_to_file(definition, output_path)
    return service.compile(definition)


# Convenience re-exports for quick imports
__all__ = [
    "validate",
    "export_yaml",
    "compile_agent",
]
