"""
Builder error hierarchy for Ainalyn SDK.

This module defines all exceptions that can be raised during the
building process. These errors are part of the Primary Adapter layer
and provide clear, actionable feedback to developers.
"""

from __future__ import annotations


class BuilderError(Exception):
    """
    Base exception for all builder-related errors.

    This is the parent class for all errors that occur during the
    building process. It should not be raised directly; use one
    of the specific subclasses instead.

    Attributes:
        message: A human-readable error message describing what went wrong.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize a builder error.

        Args:
            message: A human-readable error message.
        """
        self.message = message
        super().__init__(message)


class MissingRequiredFieldError(BuilderError):
    """
    Raised when a required field is not set before build().

    This error indicates that the developer forgot to set a required
    field on the builder before calling build().

    Example:
        >>> builder = AgentBuilder()
        >>> builder.build()  # Missing name
        MissingRequiredFieldError: Required field 'name' is not set
    """

    def __init__(self, field_name: str, builder_type: str) -> None:
        """
        Initialize a missing required field error.

        Args:
            field_name: The name of the missing field.
            builder_type: The type of builder (e.g., "AgentBuilder").
        """
        self.field_name = field_name
        self.builder_type = builder_type
        message = (
            f"Required field '{field_name}' is not set in {builder_type}. "
            f"Please call .{field_name}(...) before .build()"
        )
        super().__init__(message)


class InvalidValueError(BuilderError):
    """
    Raised when an invalid value is provided to a builder method.

    This error indicates that the value provided doesn't meet the
    required constraints (e.g., invalid name format, invalid version).

    Example:
        >>> builder = AgentBuilder("Invalid Name")
        InvalidValueError: Invalid name 'Invalid Name': must match [a-z0-9-]+
    """

    def __init__(self, field_name: str, value: object, constraint: str) -> None:
        """
        Initialize an invalid value error.

        Args:
            field_name: The name of the field with an invalid value.
            value: The invalid value that was provided.
            constraint: Description of the constraint that was violated.
        """
        self.field_name = field_name
        self.value = value
        self.constraint = constraint
        message = f"Invalid value for '{field_name}': {value!r}. {constraint}"
        super().__init__(message)


class InvalidReferenceError(BuilderError):
    """
    Raised when a node references a non-existent resource.

    This error indicates that a node is trying to reference a module,
    prompt, or tool that hasn't been defined in the agent.

    Example:
        >>> node = NodeBuilder("process").reference("undefined-module")
        >>> # When building parent workflow/agent
        InvalidReferenceError: Node 'process' references undefined module 'undefined-module'
    """

    def __init__(
        self,
        node_name: str,
        resource_type: str,
        reference: str,
    ) -> None:
        """
        Initialize an invalid reference error.

        Args:
            node_name: The name of the node with the invalid reference.
            resource_type: The type of resource ("module", "prompt", or "tool").
            reference: The name of the undefined resource.
        """
        self.node_name = node_name
        self.resource_type = resource_type
        self.reference = reference
        message = (
            f"Node '{node_name}' references undefined {resource_type} '{reference}'. "
            f"Please ensure the {resource_type} is defined before building."
        )
        super().__init__(message)


class DuplicateNameError(BuilderError):
    """
    Raised when duplicate names are found within the same scope.

    This error indicates that multiple entities with the same name
    exist in the same scope (e.g., multiple nodes named "fetch" in
    the same workflow).

    Example:
        >>> workflow.add_node(NodeBuilder("fetch").build())
        >>> workflow.add_node(NodeBuilder("fetch").build())
        DuplicateNameError: Duplicate node name 'fetch' in workflow 'main'
    """

    def __init__(self, entity_type: str, name: str, scope: str) -> None:
        """
        Initialize a duplicate name error.

        Args:
            entity_type: The type of entity ("node", "workflow", etc.).
            name: The duplicate name.
            scope: The scope where the duplicate was found.
        """
        self.entity_type = entity_type
        self.name = name
        self.scope = scope
        message = (
            f"Duplicate {entity_type} name '{name}' in {scope}. "
            f"Each {entity_type} must have a unique name within its scope."
        )
        super().__init__(message)


class EmptyCollectionError(BuilderError):
    """
    Raised when a required collection is empty.

    This error indicates that a collection (e.g., nodes in a workflow)
    is empty when it should contain at least one element.

    Example:
        >>> workflow = WorkflowBuilder("main").build()
        EmptyCollectionError: Workflow 'main' has no nodes
    """

    def __init__(self, collection_name: str, parent_name: str) -> None:
        """
        Initialize an empty collection error.

        Args:
            collection_name: The name of the empty collection.
            parent_name: The name of the parent entity.
        """
        self.collection_name = collection_name
        self.parent_name = parent_name
        message = (
            f"{parent_name} has no {collection_name}. "
            f"At least one {collection_name[:-1]} is required."
        )
        super().__init__(message)
