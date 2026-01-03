"""
Display Information for Agent marketplace presentation.

This module defines the DisplayInfo value object that contains
metadata for presenting an Agent in the Ainalyn Marketplace.

According to the v0.2 specification, every Agent must have display
metadata including name, description, and category for marketplace
discovery and user experience.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DisplayInfo:
    """
    Display metadata for Agent marketplace presentation.

    DisplayInfo contains the human-readable information that is
    displayed to users when browsing the Ainalyn Marketplace.
    This is separate from the technical Agent definition.

    Attributes:
        name: Human-readable display name for the Agent.
            This is shown as the title in marketplace listings.
            Should be concise and descriptive (e.g., "PDF Parser", "Meeting Transcriber").
        description: Full description of what the Agent does.
            Shown in the Agent detail view. Should explain capabilities,
            use cases, and any important notes for users.
        category: Marketplace category for discovery.
            Examples: "productivity", "finance", "developer-tools", "ai-ml",
            "data-processing", "communication", "document", "media".
        icon: Optional icon identifier for visual representation.
            Can be a URL or a platform-defined icon key.

    Example:
        >>> display = DisplayInfo(
        ...     name="Meeting Transcriber",
        ...     description="Transcribes meeting recordings to structured text with speaker labels and timestamps.",
        ...     category="productivity",
        ...     icon="microphone",
        ... )
    """

    name: str
    description: str
    category: str
    icon: str | None = None
