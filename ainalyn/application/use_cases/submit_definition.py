"""
Use case for submitting Agent Definitions to Platform Core.

This module implements the submission use case that orchestrates
validation, export, and Platform Core API communication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.domain.errors import SubmissionError

if TYPE_CHECKING:
    from ainalyn.application.ports.inbound.validate_agent_definition import (
        IValidateAgentDefinition,
    )
    from ainalyn.application.ports.outbound.definition_serialization import (
        IDefinitionSerializer,
    )
    from ainalyn.application.ports.outbound.platform_submission import (
        IPlatformClient,
        SubmissionOptions,
    )
    from ainalyn.domain.entities import AgentDefinition, SubmissionResult


class SubmitDefinitionUseCase:
    """
    Use case for submitting Agent Definitions to Platform Core.

    This use case orchestrates the complete submission workflow:
    1. Validate the Agent Definition (SDK-level validation)
    2. Export to YAML format (serialization)
    3. Submit to Platform Core API (network communication)

    Per Platform Constitution (rule-docs/Platform Vision & System Boundary.md):
    - SDK can submit but NOT approve agents
    - Platform Core has final authority over acceptance
    - Submission does NOT create an Execution
    - Submission does NOT incur billing (unless platform policy states)

    Per SOLID Principles:
    - Single Responsibility: Orchestrates submission workflow only
    - Dependency Inversion: Depends on abstractions (ports), not concrete implementations
    - Open/Closed: Extensible through dependency injection

    Per Clean Architecture:
    - Application layer use case (business logic orchestration)
    - Depends on domain entities and application ports
    - Independent of infrastructure details (HTTP, database, etc.)

    Example:
        >>> from ainalyn.adapters.outbound import YamlExporter, HttpPlatformClient
        >>> from ainalyn.application.use_cases import (
        ...     ValidateDefinitionUseCase,
        ...     SubmitDefinitionUseCase
        ... )
        >>> validator = ValidateDefinitionUseCase(...)
        >>> exporter = YamlExporter()
        >>> client = HttpPlatformClient()
        >>> use_case = SubmitDefinitionUseCase(validator, exporter, client)
        >>> result = use_case.execute(
        ...     definition=agent,
        ...     api_key="dev_sk_abc123"
        ... )
        >>> print(f"Review ID: {result.review_id}")
    """

    def __init__(
        self,
        validator: IValidateAgentDefinition,
        serializer: IDefinitionSerializer,
        platform_client: IPlatformClient,
    ) -> None:
        """
        Initialize the submit definition use case.

        Args:
            validator: Validator for Agent Definition (schema + static analysis).
            serializer: Serializer for converting definition to YAML.
            platform_client: Client for communicating with Platform Core API.

        Example:
            >>> use_case = SubmitDefinitionUseCase(
            ...     validator=ValidateDefinitionUseCase(...),
            ...     serializer=YamlExporter(),
            ...     platform_client=HttpPlatformClient()
            ... )
        """
        self._validator = validator
        self._serializer = serializer
        self._platform_client = platform_client

    def execute(
        self,
        definition: AgentDefinition,
        api_key: str,
        options: SubmissionOptions | None = None,
    ) -> SubmissionResult:
        """
        Execute the submission workflow.

        This method performs the complete submission process:
        1. Validates the definition using SDK rules
        2. Exports to YAML format (required by Platform Core)
        3. Submits to Platform Core API via platform client

        Validation Phase:
        - If SDK validation fails, raises SubmissionError immediately
        - SDK validation success does NOT guarantee platform acceptance
        - Platform Core applies additional validation (security, governance)

        Submission Phase:
        - Communicates with Platform Core API via platform client
        - Platform client handles authentication, retries, timeouts
        - Returns SubmissionResult with review_id for tracking

        Args:
            definition: The AgentDefinition to submit.
            api_key: Developer API key for authentication.
            options: Optional submission configuration (auto_deploy, environment, etc.).

        Returns:
            SubmissionResult: Result containing:
                - review_id: Unique ID for tracking review status
                - status: Initial status (typically PENDING_REVIEW)
                - tracking_url: URL to track progress in Developer Console
                - feedback: Any immediate feedback from Platform Core

        Raises:
            SubmissionError: If SDK validation fails. The error contains
                validation_errors attribute with details.
            AuthenticationError: If api_key is invalid or expired.
            NetworkError: If network communication with Platform Core fails.

        Example:
            >>> try:
            ...     result = use_case.execute(
            ...         definition=my_agent,
            ...         api_key="dev_sk_abc123",
            ...         options=SubmissionOptions(auto_deploy=True)
            ...     )
            ...     print(f"Submitted! Review ID: {result.review_id}")
            ...     print(f"Track at: {result.tracking_url}")
            ... except SubmissionError as e:
            ...     print(f"Submission failed: {e.message}")
            ...     if e.validation_errors:
            ...         for err in e.validation_errors:
            ...             print(f"  - {err.code}: {err.message}")

        Platform Constitution Compliance:
            This method ONLY submits for review. It does NOT:
            - Approve the agent (Platform Core's authority)
            - Create an Execution (only Platform Core creates Executions)
            - Incur billing (unless platform policy explicitly states)
            - Bypass platform governance (security, compliance checks)
        """
        # Step 1: Validate the definition
        validation_result = self._validator.execute(definition)

        if not validation_result.is_valid:
            # Convert validation errors to tuple for SubmissionError
            error_details = tuple(validation_result.errors)
            raise SubmissionError(
                message=(
                    f"Cannot submit invalid Agent Definition. "
                    f"Found {len(error_details)} validation error(s). "
                    f"Fix these issues and try again."
                ),
                validation_errors=error_details,
            )

        # Step 2: Export to YAML (Platform Core expects YAML format)
        # Note: We don't need the YAML string in this use case,
        # but the platform client will serialize it internally.
        # This step verifies serialization works before network call.
        _ = self._serializer.serialize(definition)

        # Step 3: Submit to Platform Core
        return self._platform_client.submit_agent(
            definition=definition,
            api_key=api_key,
            options=options,
        )


class TrackSubmissionUseCase:
    """
    Use case for tracking submission status.

    This use case retrieves the current status of a previously
    submitted Agent Definition from Platform Core.

    Per SOLID Principles:
    - Single Responsibility: Retrieves submission status only
    - Dependency Inversion: Depends on IPlatformClient abstraction

    Example:
        >>> use_case = TrackSubmissionUseCase(platform_client)
        >>> result = use_case.execute(
        ...     review_id="review_abc123",
        ...     api_key="dev_sk_abc123"
        ... )
        >>> print(f"Status: {result.status.value}")
        >>> if result.is_live:
        ...     print(f"Agent is live: {result.marketplace_url}")
    """

    def __init__(self, platform_client: IPlatformClient) -> None:
        """
        Initialize the track submission use case.

        Args:
            platform_client: Client for communicating with Platform Core API.
        """
        self._platform_client = platform_client

    def execute(
        self,
        review_id: str,
        api_key: str,
    ) -> SubmissionResult:
        """
        Retrieve the current status of a submission.

        Args:
            review_id: The review ID returned from submit_agent().
            api_key: Developer API key for authentication.

        Returns:
            SubmissionResult: Current status, feedback, and if approved,
                the agent_id and marketplace URL.

        Raises:
            AuthenticationError: If api_key is invalid.
            NetworkError: If network communication fails.
            SubmissionError: If review_id is not found or other errors.

        Example:
            >>> result = use_case.execute(
            ...     review_id="review_abc123",
            ...     api_key="dev_sk_abc123"
            ... )
            >>> if result.status == SubmissionStatus.ACCEPTED:
            ...     print(f"Agent ID: {result.agent_id}")
            ... elif result.status == SubmissionStatus.REJECTED:
            ...     for feedback in result.get_blocking_issues():
            ...         print(f"[ERROR] {feedback.message}")
        """
        return self._platform_client.get_submission_status(
            review_id=review_id,
            api_key=api_key,
        )
