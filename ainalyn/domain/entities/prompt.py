from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Prompt:
    """
    A reusable prompt template for LLM interactions.

    Prompt represents a template that defines how to interact with
    Language Models. It supports variable interpolation using the
    {{variable}} syntax, allowing dynamic content injection.

    This is a pure description entity. The actual LLM invocation
    is handled by Platform Core during Execution.

    Attributes:
        name: Unique identifier for this Prompt within the AgentDefinition.
            Must match pattern [a-z0-9-]+.
        description: Human-readable description of this Prompt's purpose.
        template: The prompt template content. Variables are specified
            using {{variable_name}} syntax and will be interpolated
            at execution time.
        variables: Tuple of variable names used in the template.
            Each variable listed here should appear in the template
            as {{variable_name}}.

    Example:
        >>> prompt = Prompt(
        ...     name="data-analyzer",
        ...     description="Analyzes structured data and provides insights",
        ...     template=\"\"\"
        ...     Please analyze the following data:
        ...
        ...     {{data}}
        ...
        ...     Provide insights focusing on: {{focus_areas}}
        ...     \"\"\",
        ...     variables=("data", "focus_areas"),
        ... )
    """

    name: str
    description: str
    template: str
    variables: tuple[str, ...] = ()
