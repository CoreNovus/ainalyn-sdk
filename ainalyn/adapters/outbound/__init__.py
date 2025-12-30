"""
Outbound adapters for Ainalyn SDK.

Outbound adapters (also known as driven/secondary adapters) implement
the outbound port interfaces defined in application/ports/outbound.
They handle interactions with external systems and technologies.

These adapters implement:
- IDefinitionSchemaValidator: Schema validation for Agent Definitions
- IDefinitionAnalyzer: Static analysis for Agent Definitions
- IDefinitionSerializer: YAML serialization for Agent Definitions
- IDefinitionWriter: File persistence for serialized definitions
- IPlatformClient: Platform Core API communication for submissions

Examples:
- SchemaValidator: Validates definition structure against SDK rules
- StaticAnalyzer: Performs logical consistency checks
- YamlExporter: Serializes definitions to YAML format
- MockPlatformClient: Mock Platform Core API client for testing
- HttpPlatformClient: HTTP Platform Core API client (placeholder)
"""

from __future__ import annotations

from ainalyn.adapters.outbound.http_platform_client import HttpPlatformClient
from ainalyn.adapters.outbound.mock_platform_client import MockPlatformClient
from ainalyn.adapters.outbound.schema_validator import SchemaValidator
from ainalyn.adapters.outbound.static_analyzer import StaticAnalyzer
from ainalyn.adapters.outbound.yaml_serializer import YamlExporter

__all__ = [
    "SchemaValidator",
    "StaticAnalyzer",
    "YamlExporter",
    "MockPlatformClient",
    "HttpPlatformClient",
]
