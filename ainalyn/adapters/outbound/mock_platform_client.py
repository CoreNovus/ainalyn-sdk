"""
Mock Platform Client for testing and development.

This module provides a mock implementation of the Platform Core API client
for use during development and testing before the real API is available.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from ainalyn.domain.entities.review_feedback import (
    FeedbackCategory,
    FeedbackSeverity,
    ReviewFeedback,
)
from ainalyn.domain.entities.submission_result import SubmissionResult
from ainalyn.domain.entities.submission_status import SubmissionStatus
from ainalyn.domain.errors import AuthenticationError, NetworkError

if TYPE_CHECKING:
    from ainalyn.application.ports.outbound.platform_submission import (
        SubmissionOptions,
    )
    from ainalyn.domain.entities import AgentDefinition


class MockPlatformClient:
    """
    Mock implementation of Platform Core API client.

    This mock client simulates Platform Core behavior for testing
    and development purposes. It does NOT communicate with a real API.

    Features:
    - Simulates successful submissions (returns PENDING_REVIEW status)
    - Simulates authentication failures for specific API keys
    - Simulates network errors for specific agent names
    - Generates realistic review IDs and timestamps
    - Provides sample feedback for educational purposes

    Usage:
        >>> client = MockPlatformClient()
        >>> result = client.submit_agent(
        ...     definition=my_agent,
        ...     api_key="dev_mock_123"
        ... )
        >>> print(result.review_id)  # "review_mock_..."

    Special Behaviors:
        - api_key="invalid" → raises AuthenticationError
        - agent name="network-error-test" → raises NetworkError
        - agent name="rejected-test" → returns REJECTED status with feedback
        - All other cases → returns PENDING_REVIEW status

    Per Platform Constitution:
        This is a MOCK. Real Platform Core has sole authority over
        agent acceptance, execution, and billing.
    """

    def __init__(self, simulate_delay: bool = False) -> None:
        """
        Initialize the mock platform client.

        Args:
            simulate_delay: If True, simulate network latency (not implemented).
                Reserved for future enhancement.
        """
        self._simulate_delay = simulate_delay
        # In-memory storage for tracking submissions
        self._submissions: dict[str, SubmissionResult] = {}

    def submit_agent(
        self,
        definition: AgentDefinition,
        api_key: str,
        options: SubmissionOptions | None = None,
    ) -> SubmissionResult:
        """
        Mock implementation of agent submission.

        Simulates Platform Core API behavior without making real network calls.

        Args:
            definition: The AgentDefinition to submit.
            api_key: Developer API key (use "invalid" to simulate auth failure).
            options: Optional submission configuration (currently ignored).

        Returns:
            SubmissionResult: Mock submission result.

        Raises:
            AuthenticationError: If api_key == "invalid".
            NetworkError: If definition.name == "network-error-test".

        Example:
            >>> client = MockPlatformClient()
            >>> result = client.submit_agent(
            ...     definition=agent,
            ...     api_key="dev_mock_123"
            ... )
            >>> print(result.status)
            SubmissionStatus.PENDING_REVIEW
        """
        # Simulate authentication check
        if api_key == "invalid":
            raise AuthenticationError("Invalid API key: Authentication failed")

        # Simulate network error
        if definition.name == "network-error-test":
            raise NetworkError(
                message="Failed to connect to Platform Core API",
                original_error=ConnectionError("Connection timeout"),
            )

        # Generate mock review ID
        review_id = f"review_mock_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        # Simulate rejection case
        if definition.name == "rejected-test":
            result = SubmissionResult(
                review_id=review_id,
                status=SubmissionStatus.REJECTED,
                submitted_at=timestamp,
                agent_id=None,
                agent_version_id=None,
                tracking_url=f"https://console.ainalyn.io/reviews/{review_id}",
                marketplace_url=None,
                feedback=(
                    ReviewFeedback(
                        category=FeedbackCategory.SECURITY,
                        severity=FeedbackSeverity.ERROR,
                        message=(
                            "Agent name 'rejected-test' violates naming policy. "
                            "Please use a production-appropriate name."
                        ),
                        path="agent.name",
                        code="POLICY001",
                    ),
                ),
                estimated_review_time=None,
            )
            self._submissions[review_id] = result
            return result

        # Default: successful submission (pending review)
        result = SubmissionResult(
            review_id=review_id,
            status=SubmissionStatus.PENDING_REVIEW,
            submitted_at=timestamp,
            agent_id=None,  # Not assigned yet
            agent_version_id=None,
            tracking_url=f"https://console.ainalyn.io/reviews/{review_id}",
            marketplace_url=None,
            feedback=(
                ReviewFeedback(
                    category=FeedbackCategory.QUALITY,
                    severity=FeedbackSeverity.INFO,
                    message=(
                        f"Agent '{definition.name}' has been submitted for review. "
                        f"Estimated review time: 24-48 hours."
                    ),
                    path=None,
                    code=None,
                ),
            ),
            estimated_review_time="24-48 hours",
        )

        # Store for later retrieval
        self._submissions[review_id] = result
        return result

    def get_submission_status(
        self,
        review_id: str,
        api_key: str,
    ) -> SubmissionResult:
        """
        Mock implementation of submission status retrieval.

        Simulates retrieving submission status from Platform Core.

        Args:
            review_id: The review ID from submit_agent().
            api_key: Developer API key (use "invalid" to simulate auth failure).

        Returns:
            SubmissionResult: Current mock status.

        Raises:
            AuthenticationError: If api_key == "invalid".
            SubmissionError: If review_id not found in mock storage.

        Example:
            >>> client = MockPlatformClient()
            >>> result = client.submit_agent(agent, "dev_mock_123")
            >>> status = client.get_submission_status(result.review_id, "dev_mock_123")
            >>> print(status.status)
            SubmissionStatus.PENDING_REVIEW

        Note:
            This mock does NOT simulate status transitions. All submissions
            remain in their initial status. Real Platform Core will update
            status as review progresses.
        """
        # Simulate authentication check
        if api_key == "invalid":
            raise AuthenticationError("Invalid API key: Authentication failed")

        # Check if review_id exists
        if review_id not in self._submissions:
            from ainalyn.domain.errors import SubmissionError

            raise SubmissionError(
                message=f"Review ID '{review_id}' not found. "
                f"It may have been submitted in a different session or is invalid.",
                http_status=404,
            )

        # Return stored result (no status transitions in this mock)
        return self._submissions[review_id]

    def simulate_approval(self, review_id: str) -> None:
        """
        Simulate Platform Core approving a submission.

        This is a test helper method that manually transitions
        a submission to ACCEPTED status. Real Platform Core
        controls this transition based on review process.

        Args:
            review_id: The review ID to approve.

        Raises:
            KeyError: If review_id not found.

        Example:
            >>> client = MockPlatformClient()
            >>> result = client.submit_agent(agent, "dev_mock_123")
            >>> client.simulate_approval(result.review_id)
            >>> status = client.get_submission_status(result.review_id, "dev_mock_123")
            >>> print(status.is_live)
            True
        """
        if review_id not in self._submissions:
            raise KeyError(f"Review ID '{review_id}' not found")

        original = self._submissions[review_id]
        agent_id = f"agent_mock_{uuid.uuid4().hex[:12]}"
        agent_version_id = f"av_mock_{uuid.uuid4().hex[:12]}"

        # Create approved result
        approved = SubmissionResult(
            review_id=review_id,
            status=SubmissionStatus.ACCEPTED,
            submitted_at=original.submitted_at,
            agent_id=agent_id,
            agent_version_id=agent_version_id,
            tracking_url=original.tracking_url,
            marketplace_url=f"https://marketplace.ainalyn.io/agents/{agent_id}",
            feedback=(
                ReviewFeedback(
                    category=FeedbackCategory.GENERAL,
                    severity=FeedbackSeverity.INFO,
                    message="Agent approved and deployed to marketplace",
                    path=None,
                    code=None,
                ),
            ),
            estimated_review_time=None,
        )

        self._submissions[review_id] = approved
