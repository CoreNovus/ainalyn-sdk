"""
Ainalyn Runtime Package - SDK Runtime Wrapper for ATOMIC Agents.

This package provides the runtime wrapper for ATOMIC agents, enabling
developers to write simple handler functions while the SDK handles
the communication protocol with Platform Core.

v0.2 AWS MVP Edition implements:
- @agent.atomic() decorator for handler registration
- Context parsing from Platform Core payload
- State reporting to DynamoDB (ASYNC mode)
- Standard error translation

⚠️ PLATFORM BOUNDARY WARNING ⚠️
The SDK Runtime acts as a BRIDGE between developer code and Platform Core.
It does NOT execute agents autonomously or make billing decisions.
All execution authority belongs to Platform Core.

Usage:
    from ainalyn.runtime import agent

    @agent.atomic(name="my-tool")
    def handler(input_data: dict) -> dict:
        # Your logic here
        return {"result": "success"}

    # The decorated handler is Lambda-compatible:
    # def handler(event, context) -> dict
"""

from __future__ import annotations

from ainalyn.runtime.decorators import Agent, agent

__all__ = [
    "Agent",
    "agent",
]
