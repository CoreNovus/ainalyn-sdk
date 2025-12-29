"""
Infrastructure layer for Ainalyn SDK.

This layer handles framework concerns, dependency wiring, and integration
with external systems. It sits at the outer edge of the hexagonal architecture.
"""

from __future__ import annotations

from ainalyn.infrastructure.service_factory import create_default_service

__all__ = [
    "create_default_service",
]
