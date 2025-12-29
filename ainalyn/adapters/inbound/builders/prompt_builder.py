"""
PromptBuilder - Fluent builder for Prompt entities.

⚠️ SDK BOUNDARY WARNING ⚠️
This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
Building locally does NOT mean the platform will execute it.
All execution authority belongs to Platform Core.
"""

from __future__ import annotations

from typing import Self

from ainalyn.domain.errors import (
    InvalidFormatError,
    MissingFieldError,
)
from ainalyn.domain.entities import Prompt
from ainalyn.domain.rules import DefinitionRules


class PromptBuilder:
    """
    Fluent builder for Prompt entities.

    This builder provides a convenient API for constructing Prompt
    instances with validation and clear error messages.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    This builder creates DESCRIPTIONS of agents/workflows/nodes, not executables.
    Building locally does NOT mean the platform will execute it.
    All execution authority belongs to Platform Core.

    Example:
        >>> prompt = (
        ...     PromptBuilder("data-analyzer")
        ...     .description("Analyzes structured data")
        ...     .template("Analyze this data: {{data}}")
        ...     .variables("data")
        ...     .build()
        ... )
    """

    def __init__(self, name: str) -> None:
        """
        Initialize a PromptBuilder with a name.

        Args:
            name: The unique identifier for this Prompt. Must match [a-z0-9-]+.

        Raises:
            InvalidFormatError: If the name doesn't match the required pattern.
        """
        if not DefinitionRules.is_valid_name(name):
            raise InvalidFormatError(
                "name",
                name,
                "Prompt name must start with lowercase letter and contain only "
                "lowercase letters, numbers, and hyphens",
            )
        self._name = name
        self._description: str | None = None
        self._template: str | None = None
        self._variables: list[str] = []

    def description(self, desc: str) -> Self:
        """
        Set the description for this Prompt.

        Args:
            desc: Human-readable description of this Prompt's purpose.

        Returns:
            Self: This builder for method chaining.
        """
        self._description = desc
        return self

    def template(self, tmpl: str) -> Self:
        """
        Set the prompt template content.

        Args:
            tmpl: The prompt template with {{variable}} placeholders.

        Returns:
            Self: This builder for method chaining.
        """
        self._template = tmpl
        return self

    def variables(self, *variables: str) -> Self:
        """
        Set the variables used in this template.

        Args:
            *variables: Variable names used in the template.

        Returns:
            Self: This builder for method chaining.
        """
        self._variables = list(variables)
        return self

    def build(self) -> Prompt:
        """
        Build and return an immutable Prompt entity.

        Returns:
            Prompt: A complete, immutable Prompt instance.

        Raises:
            MissingFieldError: If description or template is not set.
        """
        if self._description is None:
            raise MissingFieldError("description", "PromptBuilder")
        if self._template is None:
            raise MissingFieldError("template", "PromptBuilder")

        return Prompt(
            name=self._name,
            description=self._description,
            template=self._template,
            variables=tuple(self._variables),
        )
