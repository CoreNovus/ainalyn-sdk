"""
Inbound port for building Agent Definitions.

This module defines the interface for constructing AgentDefinition
entities, to be implemented by Primary Adapters.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition


class IDefinitionBuilder(Protocol):
    """
    Interface for building Agent Definitions (Inbound Port).

    This protocol defines the contract for constructing AgentDefinition
    entities. It is implemented by Primary Adapters such as the Fluent
    Builder API or decorator-based builders.

    The builder pattern allows for incremental construction of complex
    AgentDefinition objects with validation at build time.

    Example:
        >>> class MyBuilder:
        ...     def build(self) -> AgentDefinition:
        ...         # Construct and return AgentDefinition
        ...         ...
    """

    def build(self) -> AgentDefinition:
        """
        Build and return a complete AgentDefinition.

        This method finalizes the building process and returns an
        immutable AgentDefinition entity. It should validate that
        all required fields are present and consistent.

        Returns:
            AgentDefinition: A complete, immutable Agent definition.

        Raises:
            BuilderError: When required fields are missing or validation fails.
                Subclasses may include:
                - MissingRequiredFieldError: A required field was not set
                - InvalidReferenceError: A node references non-existent resource
                - DuplicateNameError: Duplicate names within a scope
        """
        ...
