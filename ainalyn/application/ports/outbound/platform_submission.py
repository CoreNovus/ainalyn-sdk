"""
Outbound port for Platform Core submission.

This module defines the protocol for submitting Agent Definitions
to Platform Core for review and governance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition, SubmissionResult


@dataclass(frozen=True, slots=True)
class SubmissionOptions:
    """
    Options for agent submission.

    This immutable value object contains configuration options
    for customizing the submission behavior.

    Attributes:
        auto_deploy: If True, automatically deploy the agent to
            marketplace after approval. Requires appropriate permissions.
            Defaults to False.
        environment: Target environment for submission. Common values:
            - "production": Main marketplace (default)
            - "staging": Staging environment for testing
            - "development": Development environment
        tags: Optional list of tags for categorizing the agent in
            the marketplace. Examples: ["finance", "automation", "ai"].
        private: If True, agent is only visible to the submitting
            organization. Defaults to False (public listing).

    Example:
        >>> options = SubmissionOptions(
        ...     auto_deploy=True,
        ...     environment="staging",
        ...     tags=["finance", "monitoring"],
        ...     private=False
        ... )
    """

    auto_deploy: bool = False
    environment: str = "production"
    tags: tuple[str, ...] = ()
    private: bool = False


class IPlatformClient(Protocol):
    """
    Protocol for Platform Core API client.

    This outbound port (secondary port in hexagonal architecture)
    defines the interface for communicating with Platform Core API.

    Implementations handle:
    - HTTP communication details
    - Authentication (API key management)
    - Request/response serialization
    - Error handling and retries
    - Timeout management

    Per SOLID Principles:
    - Interface Segregation: Focused on submission operations only
    - Dependency Inversion: Application depends on this abstraction,
      not concrete HTTP implementations

    Per Clean Architecture:
    - This is an outbound port in the application layer
    - Domain and application layers depend on this protocol
    - Infrastructure layer provides concrete implementations
    - Enables testing with mocks

    Example Implementation:
        >>> class HttpPlatformClient:
        ...     def submit_agent(self, definition, api_key, options):
        ...         # HTTP POST to Platform Core API
        ...         response = requests.post(...)
        ...         return SubmissionResult(...)
    """

    def submit_agent(
        self,
        definition: AgentDefinition,
        api_key: str,
        options: SubmissionOptions | None = None,
    ) -> SubmissionResult:
        """
        Submit an Agent Definition to Platform Core.

        This method sends the agent definition to Platform Core API
        for review and governance processing.

        Per Platform Constitution:
        - SDK can submit but NOT approve
        - Platform Core has final authority
        - Submission does NOT create an Execution
        - Submission does NOT incur billing (unless policy states)

        Args:
            definition: The AgentDefinition to submit.
            api_key: Developer API key for authentication.
            options: Optional submission configuration.

        Returns:
            SubmissionResult: Result containing review_id, status,
                and tracking information.

        Raises:
            AuthenticationError: If api_key is invalid or expired.
            NetworkError: If network communication fails.
            SubmissionError: If submission fails for other reasons
                (validation, quota, policy violations).

        Example:
            >>> client = HttpPlatformClient()
            >>> result = client.submit_agent(
            ...     definition=my_agent,
            ...     api_key="dev_sk_abc123",
            ...     options=SubmissionOptions(auto_deploy=False)
            ... )
            >>> print(result.review_id)
            review_abc123
        """
        ...

    def get_submission_status(
        self,
        review_id: str,
        api_key: str,
    ) -> SubmissionResult:
        """
        Retrieve the current status of a submission.

        This method queries Platform Core for the latest status
        of a previously submitted agent.

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
            >>> client = HttpPlatformClient()
            >>> result = client.get_submission_status(
            ...     review_id="review_abc123",
            ...     api_key="dev_sk_abc123"
            ... )
            >>> if result.status == SubmissionStatus.ACCEPTED:
            ...     print(f"Agent is live: {result.marketplace_url}")
        """
        ...
