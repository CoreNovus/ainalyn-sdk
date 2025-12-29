"""
Service factory for dependency injection.

This module provides factory functions for creating application services
with their required dependencies properly wired. This isolates the
concrete adapter selection from the application core.
"""

from __future__ import annotations

from ainalyn.adapters.outbound.schema_validator import SchemaValidator
from ainalyn.adapters.outbound.static_analyzer import StaticAnalyzer
from ainalyn.adapters.outbound.yaml_serializer import YamlExporter
from ainalyn.application.services import DefinitionService


def create_default_service() -> DefinitionService:
    """
    Create DefinitionService with default adapter implementations.

    This factory isolates the wiring of concrete adapters to ports.
    It provides the default configuration used by most SDK consumers.
    Advanced users can create custom services with their own adapters
    by directly instantiating DefinitionService with custom dependencies.

    Returns:
        DefinitionService: A fully configured service instance with
            default adapters (SchemaValidator, StaticAnalyzer, YamlExporter).

    Example:
        >>> from ainalyn.infrastructure import create_default_service
        >>> service = create_default_service()
        >>> result = service.validate(agent_definition)
        >>> if result.is_valid:
        ...     print("Valid!")

    Note:
        This function creates a new service instance each time it's called.
        For module-level singleton behavior, use the api.py facade functions
        (validate, export_yaml, compile_agent) which maintain a cached instance.
    """
    # Create concrete adapter instances
    schema_validator = SchemaValidator()
    static_analyzer = StaticAnalyzer()
    yaml_serializer = YamlExporter()

    # Wire adapters into the service through dependency injection
    # The service depends on port interfaces (abstractions), not concrete classes
    return DefinitionService(
        schema_validator=schema_validator,
        static_analyzer=static_analyzer,
        serializer=yaml_serializer,
        writer=None,  # File writing is handled externally for now
    )
