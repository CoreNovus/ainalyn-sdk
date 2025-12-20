"""
Adapters for Ainalyn SDK.

Adapters connect the application core to external systems and
user interfaces. They are divided into two categories:

Primary Adapters (Driving):
    Entry points for external actors to interact with the application.
    They call the application through inbound ports.

Secondary Adapters (Driven):
    Used by the application to interact with external systems.
    They implement the outbound ports called by the application.

This module will export adapters as they are implemented in
subsequent issues.
"""

from __future__ import annotations

__all__: list[str] = []
