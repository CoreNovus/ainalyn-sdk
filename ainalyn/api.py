"""
High-level API functions for Ainalyn SDK.

This module provides convenient wrapper functions around the
DefinitionService, offering a simplified API for common operations.

These functions are designed for ease of use and quick integration,
abstracting away the service initialization details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.infrastructure.service_factory import create_default_service

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.application.services import DefinitionService
    from ainalyn.application.use_cases.compile_definition import CompilationResult
    from ainalyn.application.ports.outbound.platform_submission import (
        SubmissionOptions,
    )
    from ainalyn.domain.entities import AgentDefinition, SubmissionResult
    from ainalyn.application.ports.inbound.validate_agent_definition import (
        ValidationResult,
    )


# Module-level service instance (singleton pattern)
_service: DefinitionService | None = None


def _get_service() -> DefinitionService:
    """
    Get or create the module-level DefinitionService instance.

    Uses the infrastructure factory to create a service with default
    adapter implementations. This provides consistent behavior across
    all high-level API functions.
    """
    global _service
    if _service is None:
        _service = create_default_service()
    return _service


def validate(definition: AgentDefinition) -> ValidationResult:
    """
    Validate an AgentDefinition.

    This function performs comprehensive validation including:
    - Schema validation (structural correctness)
    - Static analysis (logical consistency)

    Args:
        definition: The AgentDefinition to validate.

    Returns:
        ValidationResult: Contains all errors and warnings found.
            Use result.is_valid to check if validation passed.

    Example:
        >>> from ainalyn import AgentBuilder, validate
        >>> agent = AgentBuilder("my-agent").version("1.0.0").description("Test").build()
        >>> result = validate(agent)
        >>> if result.is_valid:
        ...     print("Validation passed!")
        ... else:
        ...     for error in result.errors:
        ...         print(f"{error.code}: {error.message}")
    """
    service = _get_service()
    return service.validate(definition)


def export_yaml(definition: AgentDefinition) -> str:
    """
    Export an AgentDefinition to YAML string.

    This function converts the AgentDefinition into a YAML-formatted
    string representation without performing validation. For a safer
    workflow that includes validation, use compile_agent() instead.

    Args:
        definition: The AgentDefinition to export.

    Returns:
        str: The YAML-formatted string representation.

    Warning:
        This function does not validate the definition before export.
        Use compile_agent() for a complete validate-and-export workflow.

    Example:
        >>> from ainalyn import AgentBuilder, export_yaml
        >>> agent = AgentBuilder("my-agent").version("1.0.0").description("Test").build()
        >>> yaml_string = export_yaml(agent)
        >>> print(yaml_string)
    """
    service = _get_service()
    return service.export(definition)


def compile_agent(
    definition: AgentDefinition,
    output_path: Path | None = None,
) -> CompilationResult:
    """
    Compile an AgentDefinition with validation and export.

    This function performs the complete compilation workflow:
    1. Validate the definition (schema + static analysis)
    2. Export to YAML (only if validation passes)
    3. Optionally write to file

    Args:
        definition: The AgentDefinition to compile.
        output_path: Optional file path to write the YAML output.
            If None, only returns the YAML string without writing.

    Returns:
        CompilationResult: Contains validation result, YAML content,
            and output path (if file was written).

    Important:
        The output of this function is an Agent Definition for platform
        submission. **Local compilation does NOT equal platform execution.**
        The actual execution is handled exclusively by Platform Core.

    Example:
        >>> from ainalyn import AgentBuilder, compile_agent
        >>> from pathlib import Path
        >>> agent = AgentBuilder("my-agent").version("1.0.0").description("Test").build()
        >>> # Compile to string
        >>> result = compile_agent(agent)
        >>> if result.is_successful:
        ...     print(result.yaml_content)
        >>> # Compile to file
        >>> result = compile_agent(agent, Path("agent.yaml"))
        >>> if result.is_successful:
        ...     print(f"Compiled to {result.output_path}")
        ... else:
        ...     for error in result.validation_result.errors:
        ...         print(f"{error.code}: {error.message}")
    """
    service = _get_service()
    if output_path is not None:
        return service.compile_to_file(definition, output_path)
    return service.compile(definition)


def submit_agent(
    definition: AgentDefinition,
    api_key: str,
    *,
    base_url: str | None = None,
    auto_deploy: bool = False,
) -> SubmissionResult:
    """
    Submit an Agent Definition to Platform Core for review.

    This function performs the complete submission workflow:
    1. Validates the definition (SDK-level validation)
    2. Exports to YAML format
    3. Submits to Platform Core API

    Important - Platform Constitution Compliance:
    - SDK can submit but NOT approve (Platform Core has final authority)
    - Submission does NOT create an Execution
    - Submission does NOT incur billing (unless platform policy states)

    Args:
        definition: The AgentDefinition to submit.
        api_key: Developer API key for authentication.
            Get yours at: https://console.ainalyn.io/api-keys
        base_url: Optional Platform Core API base URL.
            Defaults to production: https://api.ainalyn.io
            Use for testing: https://staging-api.ainalyn.io
        auto_deploy: If True, automatically deploy after approval.
            Requires appropriate permissions. Defaults to False.

    Returns:
        SubmissionResult: Contains review_id, status, and tracking URL.
            - review_id: Use with track_submission() to check status
            - status: Initial status (typically PENDING_REVIEW)
            - tracking_url: URL to track progress in Developer Console
            - feedback: Any immediate feedback from Platform Core

    Raises:
        SubmissionError: If submission fails due to validation or network.
            The error contains validation_errors attribute with details.
        AuthenticationError: If api_key is invalid or expired.
        NetworkError: If network communication with Platform Core fails.

    Example:
        >>> from ainalyn import AgentBuilder, submit_agent
        >>> agent = AgentBuilder("my-agent").version("1.0.0").build()
        >>> result = submit_agent(agent, api_key="dev_sk_abc123")
        >>> if result.is_accepted:
        ...     print(f"Submitted for review!")
        ...     print(f"Review ID: {result.review_id}")
        ...     print(f"Track at: {result.tracking_url}")
        ... else:
        ...     print(f"Submission rejected")
        ...     for feedback in result.feedback:
        ...         print(f"  - {feedback.message}")

    Note:
        Currently uses MockPlatformClient for testing until Platform Core
        API is available. Real HTTP communication will be enabled in future.
    """
    from ainalyn.application.ports.outbound.platform_submission import (
        SubmissionOptions,
    )

    service = _get_service()
    options = SubmissionOptions(
        auto_deploy=auto_deploy,
        environment="production" if base_url is None else "custom",
        base_url=base_url,
    )
    return service.submit(definition, api_key, options)


def track_submission(
    review_id: str,
    api_key: str,
    *,
    base_url: str | None = None,
) -> SubmissionResult:
    """
    Track the status of a submitted Agent Definition.

    This function queries Platform Core for the current status
    of a previously submitted agent.

    Args:
        review_id: The review ID returned from submit_agent().
        api_key: Developer API key for authentication.
        base_url: Optional Platform Core API base URL.
            Defaults to production: https://api.ainalyn.io

    Returns:
        SubmissionResult: Current status and feedback.
            - status: Current review status (PENDING_REVIEW, ACCEPTED, REJECTED)
            - agent_id: Assigned if status is ACCEPTED
            - marketplace_url: URL if agent is live
            - feedback: Feedback from Platform Core's review process

    Raises:
        AuthenticationError: If api_key is invalid.
        NetworkError: If network communication fails.
        SubmissionError: If review_id is not found or other errors.

    Example:
        >>> from ainalyn import track_submission, SubmissionStatus
        >>> result = track_submission(
        ...     review_id="review_abc123",
        ...     api_key="dev_sk_abc123"
        ... )
        >>> print(f"Status: {result.status.value}")
        >>> if result.is_live:
        ...     print(f"Agent is live: {result.marketplace_url}")
        ... elif result.is_rejected:
        ...     print("Rejected. Feedback:")
        ...     for issue in result.get_blocking_issues():
        ...         print(f"  [{issue.severity.value}] {issue.message}")

    Note:
        Currently uses MockPlatformClient for testing until Platform Core
        API is available. Real HTTP communication will be enabled in future.
    """
    service = _get_service()
    return service.track_submission(review_id, api_key)


# Convenience re-exports for quick imports
__all__ = [
    "validate",
    "export_yaml",
    "compile_agent",
    "submit_agent",
    "track_submission",
]
