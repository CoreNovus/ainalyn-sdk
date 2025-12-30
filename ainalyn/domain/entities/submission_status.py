"""
Submission Status Value Object.

This module defines the status of an Agent Definition submission
to Platform Core for review and governance.
"""

from __future__ import annotations

from enum import Enum


class SubmissionStatus(Enum):
    """
    Status of an Agent Definition submission to Platform Core.

    This enum represents the lifecycle states of a submission as it
    progresses through Platform Core's review and governance process.

    Per Platform Constitution (rule-docs/Platform Vision & System Boundary.md):
    - SDK can submit but NOT approve
    - Platform Core has final authority over acceptance
    - Submission does NOT create an Execution

    Attributes:
        PENDING_REVIEW: Submission accepted and awaiting platform review.
            This is the typical initial state after successful submission.
        ACCEPTED: Submission approved by Platform Core and agent is live
            in the marketplace. An agent_id has been assigned.
        REJECTED: Submission rejected by Platform Core due to policy,
            security, or quality issues. Feedback will contain reasons.
        DRAFT: Submission saved as draft but not yet submitted for review.
            This state is for future functionality.

    Example:
        >>> status = SubmissionStatus.PENDING_REVIEW
        >>> print(status.value)
        pending_review
        >>> if status in (SubmissionStatus.PENDING_REVIEW, SubmissionStatus.ACCEPTED):
        ...     print("Submission was accepted")
    """

    PENDING_REVIEW = "pending_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DRAFT = "draft"

    def is_terminal(self) -> bool:
        """
        Check if this status is a terminal state.

        Terminal states are final and will not change:
        - ACCEPTED: Agent is live
        - REJECTED: Agent was rejected

        Non-terminal states may transition:
        - PENDING_REVIEW: May become ACCEPTED or REJECTED
        - DRAFT: May be submitted to become PENDING_REVIEW

        Returns:
            bool: True if this is a terminal state.

        Example:
            >>> SubmissionStatus.ACCEPTED.is_terminal()
            True
            >>> SubmissionStatus.PENDING_REVIEW.is_terminal()
            False
        """
        return self in (SubmissionStatus.ACCEPTED, SubmissionStatus.REJECTED)

    def is_successful(self) -> bool:
        """
        Check if this status represents a successful submission.

        A successful submission means Platform Core has accepted it
        for review or approved it for marketplace listing.

        Returns:
            bool: True if submission was accepted (pending or approved).

        Example:
            >>> SubmissionStatus.ACCEPTED.is_successful()
            True
            >>> SubmissionStatus.REJECTED.is_successful()
            False
        """
        return self in (SubmissionStatus.PENDING_REVIEW, SubmissionStatus.ACCEPTED)
