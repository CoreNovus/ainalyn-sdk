"""
Service factory for dependency injection.

This module provides factory functions for creating application services
with their required dependencies properly wired. This isolates the
concrete adapter selection from the application core.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.adapters.outbound.mock_platform_client import MockPlatformClient
from ainalyn.adapters.outbound.schema_validator import SchemaValidator
from ainalyn.adapters.outbound.static_analyzer import StaticAnalyzer
from ainalyn.adapters.outbound.yaml_serializer import YamlExporter
from ainalyn.application.services import DefinitionService

if TYPE_CHECKING:
    from ainalyn.application.ports.outbound.platform_submission import IPlatformClient


def create_default_service(
    with_mock_platform_client: bool = True,
) -> DefinitionService:
    """
    Create DefinitionService with default adapter implementations.

    This factory isolates the wiring of concrete adapters to ports.
    It provides the default configuration used by most SDK consumers.
    Advanced users can create custom services with their own adapters
    by directly instantiating DefinitionService with custom dependencies.

    Args:
        with_mock_platform_client: If True, includes MockPlatformClient
            for submission features. If False, submission methods will
            raise RuntimeError. Defaults to True for convenience.

    Returns:
        DefinitionService: A fully configured service instance with
            default adapters (SchemaValidator, StaticAnalyzer, YamlExporter,
            and optionally MockPlatformClient).

    Example:
        >>> from ainalyn.infrastructure import create_default_service
        >>> # With submission support (uses MockPlatformClient)
        >>> service = create_default_service()
        >>> result = service.validate(agent_definition)
        >>> if result.is_valid:
        ...     print("Valid!")
        >>>
        >>> # Without submission support
        >>> service = create_default_service(with_mock_platform_client=False)

    Note:
        This function creates a new service instance each time it's called.
        For module-level singleton behavior, use the api.py facade functions
        (validate, export_yaml, compile_agent, submit_agent) which maintain
        a cached instance.

    Platform Client Selection:
        - Default: Uses MockPlatformClient (for testing/development)
        - Production: When Platform Core API is ready, replace with
          HttpPlatformClient via custom factory or environment variable
    """
    # Create concrete adapter instances
    schema_validator = SchemaValidator()
    static_analyzer = StaticAnalyzer()
    yaml_serializer = YamlExporter()

    # Create platform client if requested
    platform_client: IPlatformClient | None = None
    if with_mock_platform_client:
        platform_client = MockPlatformClient()

    # Wire adapters into the service through dependency injection
    # The service depends on port interfaces (abstractions), not concrete classes
    return DefinitionService(
        schema_validator=schema_validator,
        static_analyzer=static_analyzer,
        serializer=yaml_serializer,
        writer=None,  # File writing is handled externally for now
        platform_client=platform_client,
    )
