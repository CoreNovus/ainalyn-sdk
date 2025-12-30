"""
Domain error hierarchy for Ainalyn SDK.

This module defines all exceptions that represent domain rule violations
during Agent Definition compilation (description-time errors).

⚠️ CRITICAL PLATFORM BOUNDARY WARNING ⚠️

These errors indicate issues with the Agent Definition structure during SDK
compilation. They are NOT execution errors from the platform runtime.

- These are compile-time/description-time errors from the SDK
- They indicate structural or semantic issues in the definition
- They do NOT represent platform execution failures
- SDK validation success ≠ Platform will execute this definition

Platform Core applies additional validation during submission and has sole
authority over execution.

Per platform constitution: "SDK is a Compiler, NOT a Runtime"
See: https://docs.ainalyn.io/sdk/platform-boundaries/
"""

from __future__ import annotations


class DomainError(Exception):
    """
    Base exception for all domain-related errors.

    This is the parent class for all errors that occur due to domain
    rule violations during Agent Definition compilation. It should not
    be raised directly; use one of the specific subclasses instead.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    These errors occur during local compilation and do not represent
    platform execution failures. The platform may apply additional
    validation when you submit the definition.

    Attributes:
        message: A human-readable error message describing what went wrong.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize a domain error.

        Args:
            message: A human-readable error message.
        """
        self.message = message
        super().__init__(message)


class DefinitionError(DomainError):
    """
    Base error for Agent Definition compilation issues.

    ⚠️ IMPORTANT: Compile-Time vs Execution-Time ⚠️

    These are compile-time/description-time errors from the SDK.
    They indicate issues with the Agent Definition structure, NOT execution failures.

    Examples of what these errors represent:
    - Missing required fields in the definition
    - Invalid field formats (names, versions)
    - Broken references between definition components
    - Structural issues (cycles, unreachable nodes)

    Examples of what these errors DO NOT represent:
    - Agent execution failures on the platform
    - Tool invocation errors during runtime
    - Resource quota violations
    - Platform governance policy violations

    Platform Core may apply additional validation during submission.
    SDK validation success does NOT guarantee platform execution.

    Per platform constitution: "Local compilation ≠ Platform execution"
    See: https://docs.ainalyn.io/sdk/platform-boundaries/
    """


class MissingFieldError(DefinitionError):
    """
    Required field missing in Agent Definition.

    This compile-time error indicates that a required field was not provided
    when constructing a domain entity in the Agent Definition.

    Example:
        >>> AgentDefinition(name="", version="1.0.0", ...)
        MissingFieldError: Required field 'name' cannot be empty
    """

    def __init__(self, field_name: str, entity_type: str | None = None) -> None:
        """
        Initialize a missing field error.

        Args:
            field_name: The name of the missing field.
            entity_type: Optional type of entity (e.g., "AgentDefinition").
        """
        self.field_name = field_name
        self.entity_type = entity_type
        if entity_type:
            message = (
                f"Required field '{field_name}' is missing or empty in {entity_type}"
            )
        else:
            message = f"Required field '{field_name}' is missing or empty"
        super().__init__(message)


class InvalidFormatError(DefinitionError):
    """
    Field value doesn't match required format.

    This compile-time error indicates that a field value doesn't meet
    the structural requirements (e.g., invalid name format, invalid version).

    Example:
        >>> AgentDefinition(name="Invalid Name", ...)
        InvalidFormatError: Invalid name 'Invalid Name': must match [a-z0-9-]+
    """

    def __init__(self, field_name: str, value: object, constraint: str) -> None:
        """
        Initialize an invalid format error.

        Args:
            field_name: The name of the field with an invalid value.
            value: The invalid value that was provided.
            constraint: Description of the format constraint that was violated.
        """
        self.field_name = field_name
        self.value = value
        self.constraint = constraint
        message = f"Invalid value for '{field_name}': {value!r}. {constraint}"
        super().__init__(message)


class ReferenceError(DefinitionError):
    """
    Invalid reference within Agent Definition.

    This compile-time error indicates that an entity references a resource
    (module, prompt, tool) that hasn't been defined in the agent.

    Example:
        >>> node.reference = "undefined-module"
        ReferenceError: References undefined module 'undefined-module'
    """

    def __init__(
        self,
        source: str,
        resource_type: str,
        reference: str,
    ) -> None:
        """
        Initialize a reference error.

        Args:
            source: The name of the entity with the invalid reference.
            resource_type: The type of resource ("module", "prompt", or "tool").
            reference: The name of the undefined resource.
        """
        self.source = source
        self.resource_type = resource_type
        self.reference = reference
        message = (
            f"'{source}' references undefined {resource_type} '{reference}'. "
            f"The {resource_type} must be defined in the agent."
        )
        super().__init__(message)


class DuplicateError(DefinitionError):
    """
    Duplicate names within scope.

    This compile-time error indicates that multiple entities with the same
    name exist in the same scope (e.g., multiple nodes named "fetch" in
    the same workflow).

    Example:
        >>> workflow = Workflow(nodes=(node1, node1), ...)
        DuplicateError: Duplicate node name 'fetch'
    """

    def __init__(self, entity_type: str, name: str, scope: str | None = None) -> None:
        """
        Initialize a duplicate error.

        Args:
            entity_type: The type of entity ("node", "workflow", etc.).
            name: The duplicate name.
            scope: Optional scope where the duplicate was found.
        """
        self.entity_type = entity_type
        self.name = name
        self.scope = scope
        if scope:
            message = (
                f"Duplicate {entity_type} name '{name}' in {scope}. "
                f"Each {entity_type} must have a unique name within its scope."
            )
        else:
            message = (
                f"Duplicate {entity_type} name '{name}'. "
                f"Each {entity_type} must have a unique name."
            )
        super().__init__(message)


class EmptyCollectionError(DefinitionError):
    """
    Required collection is empty.

    This compile-time error indicates that a collection (e.g., nodes in
    a workflow) is empty when it should contain at least one element.

    Example:
        >>> Workflow(name="main", nodes=(), ...)
        EmptyCollectionError: Workflow 'main' must have at least one node
    """

    def __init__(self, collection_name: str, parent_name: str) -> None:
        """
        Initialize an empty collection error.

        Args:
            collection_name: The name of the empty collection (e.g., "nodes").
            parent_name: The name of the parent entity.
        """
        self.collection_name = collection_name
        self.parent_name = parent_name
        singular = collection_name.rstrip("s")
        message = (
            f"'{parent_name}' has no {collection_name}. "
            f"At least one {singular} is required."
        )
        super().__init__(message)


class CyclicDependencyError(DefinitionError):
    """
    Workflow contains cycles (not a DAG).

    This compile-time error indicates that a workflow contains cycles,
    which violates the DAG (Directed Acyclic Graph) requirement.

    Example:
        >>> # Node A → Node B → Node C → Node A (cycle!)
        CyclicDependencyError: Workflow contains a cycle: A → B → C → A
    """

    def __init__(self, cycle_path: list[str]) -> None:
        """
        Initialize a cyclic dependency error.

        Args:
            cycle_path: The list of node names forming the cycle.
        """
        self.cycle_path = cycle_path
        cycle_str = " → ".join(cycle_path)
        message = f"Workflow contains a cycle: {cycle_str}"
        super().__init__(message)


class UnreachableNodeError(DefinitionError):
    """
    Node unreachable from entry node.

    This compile-time error indicates that a node in a workflow cannot be
    reached by following edges from the entry node.

    Example:
        >>> # Node 'orphan' has no incoming edges
        UnreachableNodeError: Node 'orphan' is unreachable from entry node
    """

    def __init__(self, node_name: str, entry_node: str) -> None:
        """
        Initialize an unreachable node error.

        Args:
            node_name: The name of the unreachable node.
            entry_node: The name of the entry node.
        """
        self.node_name = node_name
        self.entry_node = entry_node
        message = (
            f"Node '{node_name}' is unreachable from entry node '{entry_node}'. "
            f"All nodes must be reachable via edges."
        )
        super().__init__(message)


class SubmissionError(DomainError):
    """
    Error during agent submission to Platform Core.

    This error indicates issues that occur when attempting to submit
    an Agent Definition to Platform Core for review.

    ⚠️ PLATFORM BOUNDARY ⚠️
    This error represents submission-time failures, not execution failures.
    Submission does NOT create an Execution.

    Common causes:
    - Network connectivity issues
    - Authentication failures (invalid API key)
    - Platform validation failures (stricter than SDK validation)
    - Rate limiting or quota violations
    - Platform service unavailable

    Attributes:
        message: Human-readable error description.
        validation_errors: Optional tuple of ValidationError items if
            submission failed due to validation issues.
        http_status: Optional HTTP status code if this was a network error.

    Example:
        >>> try:
        ...     submit_agent(agent, api_key="invalid")
        ... except SubmissionError as e:
        ...     print(f"Submission failed: {e.message}")
        ...     if e.validation_errors:
        ...         for err in e.validation_errors:
        ...             print(f"  - {err.message}")
    """

    def __init__(
        self,
        message: str,
        validation_errors: tuple | None = None,
        http_status: int | None = None,
    ) -> None:
        """
        Initialize a submission error.

        Args:
            message: Human-readable error description.
            validation_errors: Optional tuple of ValidationError items.
            http_status: Optional HTTP status code.
        """
        self.validation_errors = validation_errors or ()
        self.http_status = http_status
        super().__init__(message)


class AuthenticationError(SubmissionError):
    """
    Authentication failure during submission.

    This error indicates that the API key provided for submission
    is invalid, expired, or lacks necessary permissions.

    Example:
        >>> try:
        ...     submit_agent(agent, api_key="invalid_key")
        ... except AuthenticationError as e:
        ...     print(f"Authentication failed: {e.message}")
    """

    def __init__(self, message: str = "Invalid or expired API key") -> None:
        """
        Initialize an authentication error.

        Args:
            message: Human-readable error description.
        """
        super().__init__(message, http_status=401)


class NetworkError(SubmissionError):
    """
    Network connectivity error during submission.

    This error indicates network-level failures when attempting to
    communicate with Platform Core API.

    Common causes:
    - Connection timeout
    - DNS resolution failure
    - Platform service unavailable
    - Network connectivity issues

    Example:
        >>> try:
        ...     submit_agent(agent, api_key="key", timeout=1)
        ... except NetworkError as e:
        ...     print(f"Network error: {e.message}")
    """

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        """
        Initialize a network error.

        Args:
            message: Human-readable error description.
            original_error: Optional original exception that caused this error.
        """
        self.original_error = original_error
        super().__init__(message)


# Legacy aliases for backward compatibility
# These will be deprecated in future versions
MissingRequiredFieldError = MissingFieldError
InvalidValueError = InvalidFormatError
InvalidReferenceError = ReferenceError
DuplicateNameError = DuplicateError
