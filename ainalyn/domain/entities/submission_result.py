"""
Submission Result Entity.

This module defines the result of submitting an Agent Definition
to Platform Core for review and governance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ainalyn.domain.entities.review_feedback import ReviewFeedback
    from ainalyn.domain.entities.submission_status import SubmissionStatus


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    """
    Result of submitting an Agent Definition to Platform Core.

    This immutable entity represents the outcome of an agent submission,
    including review status, tracking information, and feedback from
    Platform Core's review and governance process.

    Per Platform Constitution (rule-docs/Platform Vision & System Boundary.md):
    - SDK can submit but NOT approve agents
    - Platform Core has final authority over acceptance
    - Submission does NOT create an Execution
    - Submission does NOT incur billing (unless platform policy states)

    Attributes:
        review_id: Unique identifier for tracking this submission through
            the review process. Use with track_submission() to check status.
        status: Current status of the submission (pending_review, accepted,
            rejected, draft).
        submitted_at: ISO 8601 timestamp when the submission was received
            by Platform Core. Example: "2025-12-30T10:00:00Z"
        agent_id: Unique agent identifier assigned by Platform Core.
            Only present if status is ACCEPTED. Use this ID to reference
            the agent in execution requests.
        agent_version_id: Unique identifier for this specific version of
            the agent. Only present if status is ACCEPTED.
        tracking_url: URL to the Developer Console page where developers
            can track review progress and see detailed feedback.
        marketplace_url: URL to the marketplace listing for this agent.
            Only present if status is ACCEPTED.
        feedback: Tuple of ReviewFeedback items from Platform Core's
            review process. Empty if no feedback provided yet.
        estimated_review_time: Human-readable estimate of review completion
            time. Examples: "24h", "2-3 business days", "pending manual review".
            None if no estimate available.

    Example:
        >>> result = SubmissionResult(
        ...     review_id="review_abc123",
        ...     status=SubmissionStatus.PENDING_REVIEW,
        ...     submitted_at="2025-12-30T10:00:00Z",
        ...     agent_id=None,
        ...     agent_version_id=None,
        ...     tracking_url="https://console.ainalyn.io/reviews/review_abc123",
        ...     marketplace_url=None,
        ...     feedback=(),
        ...     estimated_review_time="24h"
        ... )
        >>> print(f"Review ID: {result.review_id}")
        Review ID: review_abc123
        >>> result.is_accepted
        True
    """

    review_id: str
    status: SubmissionStatus
    submitted_at: str
    agent_id: str | None
    agent_version_id: str | None
    tracking_url: str | None
    marketplace_url: str | None = None
    feedback: tuple[ReviewFeedback, ...] = ()
    estimated_review_time: str | None = None

    @property
    def is_accepted(self) -> bool:
        """
        Check if submission was accepted by Platform Core.

        A submission is considered "accepted" if it was either:
        1. Accepted for review (PENDING_REVIEW) - awaiting final decision
        2. Approved and live (ACCEPTED) - agent is in marketplace

        Note: This does NOT mean the agent is live yet if status is
        PENDING_REVIEW. Use is_live to check if agent is in marketplace.

        Returns:
            bool: True if Platform Core accepted the submission.

        Example:
            >>> pending = SubmissionResult(
            ...     review_id="r1",
            ...     status=SubmissionStatus.PENDING_REVIEW,
            ...     submitted_at="2025-12-30T10:00:00Z",
            ...     agent_id=None,
            ...     agent_version_id=None,
            ...     tracking_url="https://..."
            ... )
            >>> pending.is_accepted
            True
            >>> pending.is_live
            False
        """
        return self.status.is_successful()

    @property
    def is_live(self) -> bool:
        """
        Check if agent is live in the marketplace.

        An agent is live only when status is ACCEPTED, meaning Platform
        Core has approved it and it's available for execution.

        Returns:
            bool: True if agent is live in marketplace.

        Example:
            >>> live = SubmissionResult(
            ...     review_id="r1",
            ...     status=SubmissionStatus.ACCEPTED,
            ...     submitted_at="2025-12-30T10:00:00Z",
            ...     agent_id="agent_xyz",
            ...     agent_version_id="av_123",
            ...     tracking_url="https://...",
            ...     marketplace_url="https://marketplace.ainalyn.io/agents/agent_xyz"
            ... )
            >>> live.is_live
            True
        """
        from ainalyn.domain.entities.submission_status import SubmissionStatus

        return self.status == SubmissionStatus.ACCEPTED

    @property
    def is_rejected(self) -> bool:
        """
        Check if submission was rejected by Platform Core.

        Returns:
            bool: True if submission was rejected.

        Example:
            >>> rejected = SubmissionResult(
            ...     review_id="r1",
            ...     status=SubmissionStatus.REJECTED,
            ...     submitted_at="2025-12-30T10:00:00Z",
            ...     agent_id=None,
            ...     agent_version_id=None,
            ...     tracking_url="https://...",
            ...     feedback=(
            ...         ReviewFeedback(
            ...             category=FeedbackCategory.SECURITY,
            ...             severity=FeedbackSeverity.ERROR,
            ...             message="Security issue found"
            ...         ),
            ...     )
            ... )
            >>> rejected.is_rejected
            True
        """
        from ainalyn.domain.entities.submission_status import SubmissionStatus

        return self.status == SubmissionStatus.REJECTED

    @property
    def has_blocking_issues(self) -> bool:
        """
        Check if there are blocking issues in the feedback.

        Blocking issues are ERROR-severity feedback items that prevent
        approval. If any blocking issues exist, the submission will be
        or has been rejected.

        Returns:
            bool: True if there are ERROR-severity feedback items.

        Example:
            >>> result = SubmissionResult(
            ...     review_id="r1",
            ...     status=SubmissionStatus.REJECTED,
            ...     submitted_at="2025-12-30T10:00:00Z",
            ...     agent_id=None,
            ...     agent_version_id=None,
            ...     tracking_url="https://...",
            ...     feedback=(
            ...         ReviewFeedback(
            ...             category=FeedbackCategory.SECURITY,
            ...             severity=FeedbackSeverity.ERROR,
            ...             message="Critical issue"
            ...         ),
            ...         ReviewFeedback(
            ...             category=FeedbackCategory.QUALITY,
            ...             severity=FeedbackSeverity.WARNING,
            ...             message="Minor issue"
            ...         ),
            ...     )
            ... )
            >>> result.has_blocking_issues
            True
        """
        return any(fb.is_blocking() for fb in self.feedback)

    def get_blocking_issues(self) -> tuple[ReviewFeedback, ...]:
        """
        Get all blocking (ERROR-severity) feedback items.

        Returns:
            tuple[ReviewFeedback, ...]: All ERROR-severity feedback items.

        Example:
            >>> result = SubmissionResult(...)  # with mixed feedback
            >>> blocking = result.get_blocking_issues()
            >>> for issue in blocking:
            ...     print(f"[ERROR] {issue.message}")
        """
        return tuple(fb for fb in self.feedback if fb.is_blocking())

    def get_warnings(self) -> tuple[ReviewFeedback, ...]:
        """
        Get all warning (WARNING-severity) feedback items.

        Returns:
            tuple[ReviewFeedback, ...]: All WARNING-severity feedback items.

        Example:
            >>> result = SubmissionResult(...)  # with mixed feedback
            >>> warnings = result.get_warnings()
            >>> for warning in warnings:
            ...     print(f"[WARN] {warning.message}")
        """
        from ainalyn.domain.entities.review_feedback import FeedbackSeverity

        return tuple(fb for fb in self.feedback if fb.severity == FeedbackSeverity.WARNING)

    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            str: Summary of submission result.

        Example:
            >>> result = SubmissionResult(
            ...     review_id="review_abc123",
            ...     status=SubmissionStatus.PENDING_REVIEW,
            ...     submitted_at="2025-12-30T10:00:00Z",
            ...     agent_id=None,
            ...     agent_version_id=None,
            ...     tracking_url="https://..."
            ... )
            >>> print(result)
            SubmissionResult(review_id=review_abc123, status=pending_review)
        """
        return f"SubmissionResult(review_id={self.review_id}, status={self.status.value})"
