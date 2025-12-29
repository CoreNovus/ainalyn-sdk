"""
Ports layer for Ainalyn SDK application.

Ports define the interfaces (contracts) between the application core
and the external world. They follow hexagonal architecture principles:

- Inbound Ports: Represent use cases (what the application can do)
- Outbound Ports: Represent capabilities needed by the application

This separation ensures the application core remains independent of
implementation details.
"""

from __future__ import annotations

__all__: list[str] = []
