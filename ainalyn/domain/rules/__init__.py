"""
Domain rules for Ainalyn SDK.

This module exports domain rules that encapsulate the core business
logic for validating AgentDefinition entities.

These rules are pure functions with no external dependencies,
forming the foundation for validation in the application layer.

v0.2 AWS MVP Edition adds:
- ReviewGateRules: 5 mandatory Review Gates for Platform Core submission
- GateViolation: Represents a single gate violation
- GateCode: Enumeration of gate error codes
"""

from __future__ import annotations

from ainalyn.domain.rules.definition_rules import (
    NAME_PATTERN,
    SEMVER_PATTERN,
    DefinitionRules,
)
from ainalyn.domain.rules.review_gate_rules import (
    GateCode,
    GateViolation,
    ReviewGateRules,
)

__all__ = [
    "NAME_PATTERN",
    "SEMVER_PATTERN",
    "DefinitionRules",
    # v0.2 Review Gate rules
    "ReviewGateRules",
    "GateViolation",
    "GateCode",
]
