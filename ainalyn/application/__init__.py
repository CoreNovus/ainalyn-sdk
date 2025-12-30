"""
Application layer for Ainalyn SDK.

The application layer orchestrates the use cases by coordinating
between the domain layer and the ports. It contains:

- Use cases that implement business workflows
- Application services that compose multiple operations

This layer depends on the domain layer and defines interfaces
(ports) that are implemented by adapters.
"""

from __future__ import annotations

from ainalyn.application.ports.outbound.platform_submission import SubmissionOptions
from ainalyn.application.services import DefinitionService
from ainalyn.application.use_cases import (
    CompilationResult,
    CompileDefinitionUseCase,
    ExportDefinitionUseCase,
    SubmitDefinitionUseCase,
    TrackSubmissionUseCase,
    ValidateDefinitionUseCase,
)

__all__ = [
    # Services
    "DefinitionService",
    # Use Cases
    "ValidateDefinitionUseCase",
    "ExportDefinitionUseCase",
    "CompileDefinitionUseCase",
    "SubmitDefinitionUseCase",
    "TrackSubmissionUseCase",
    # Results
    "CompilationResult",
    # Options
    "SubmissionOptions",
]
