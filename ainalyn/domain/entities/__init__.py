"""
Domain entities for Ainalyn SDK.

This module exports all core domain entities that represent the
fundamental building blocks of an Agent Definition.

These entities are immutable (frozen dataclasses) and represent
pure description, with no execution semantics.

v0.2 AWS MVP Edition adds:
- AgentType: ATOMIC vs COMPOSITE agent classification
- DisplayInfo: Marketplace display metadata
- PricingStrategy: Monetization model description
- BehaviorConfig: Execution behavior characteristics
"""

from __future__ import annotations

from ainalyn.domain.entities.agent_definition import AgentDefinition
from ainalyn.domain.entities.agent_type import AgentType
from ainalyn.domain.entities.behavior_config import BehaviorConfig
from ainalyn.domain.entities.display_info import DisplayInfo
from ainalyn.domain.entities.eip_dependency import (
    CompletionCriteria,
    EIPBinding,
    EIPDependency,
)
from ainalyn.domain.entities.execution_context import (
    ExecutionContext,
    ExecutionMeta,
    ExecutionMode,
    InfraContext,
    SecurityContext,
)
from ainalyn.domain.entities.execution_result import (
    ExecutionResult,
    ExecutionStatus,
    PlatformErrors,
    StandardError,
)
from ainalyn.domain.entities.module import Module
from ainalyn.domain.entities.node import Node, NodeType
from ainalyn.domain.entities.pricing_strategy import (
    PricingComponent,
    PricingStrategy,
    PricingType,
)
from ainalyn.domain.entities.prompt import Prompt
from ainalyn.domain.entities.review_feedback import (
    FeedbackCategory,
    FeedbackSeverity,
    ReviewFeedback,
)
from ainalyn.domain.entities.submission_result import SubmissionResult
from ainalyn.domain.entities.submission_status import SubmissionStatus
from ainalyn.domain.entities.tool import Tool
from ainalyn.domain.entities.workflow import Workflow

__all__ = [
    "AgentDefinition",
    "Module",
    "Node",
    "NodeType",
    "Prompt",
    "Tool",
    "Workflow",
    # v0.2 Agent metadata entities
    "AgentType",
    "DisplayInfo",
    "BehaviorConfig",
    # v0.2 Pricing entities
    "PricingType",
    "PricingStrategy",
    "PricingComponent",
    # v0.2 Runtime entities
    "ExecutionContext",
    "ExecutionMeta",
    "ExecutionMode",
    "SecurityContext",
    "InfraContext",
    "ExecutionResult",
    "ExecutionStatus",
    "PlatformErrors",
    "StandardError",
    # EIP-related entities
    "EIPBinding",
    "EIPDependency",
    "CompletionCriteria",
    # Submission-related entities
    "SubmissionResult",
    "SubmissionStatus",
    "ReviewFeedback",
    "FeedbackCategory",
    "FeedbackSeverity",
]
