"""
Review Gate validation rules for v0.2 AWS MVP Edition.

This module implements the 5 mandatory Review Gates defined in the
v0.2 specification (04_agent_review_core_integration_spec.md).

Every Agent Definition must pass all 5 gates to be submitted to
Platform Core for review.

IMPORTANT: These gates are SDK-level pre-validation. Platform Core
performs additional governance, security, and resource checks.
Passing SDK gates does NOT guarantee Platform Core approval.

Gates:
1. Contract Completeness - task_goal, completion_criteria, schemas
2. No Shadow Runtime - no autonomous loops, persistent memory
3. Result Sovereignty - output from defined workflow only
4. Billing Compliance - pricing is hint only, no billing logic
5. EIP Dependency Compliance - all EIP references declared
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition


class GateCode(Enum):
    """
    Review Gate error codes.

    Each code follows the pattern GATE{N}_{ERROR_TYPE} where N is
    the gate number (1-5) and ERROR_TYPE describes the violation.
    """

    # Gate 1: Contract Completeness
    GATE1_MISSING_TASK_GOAL = "GATE1_MISSING_TASK_GOAL"
    GATE1_MISSING_COMPLETION_CRITERIA = "GATE1_MISSING_COMPLETION_CRITERIA"
    GATE1_MISSING_INPUT_SCHEMA = "GATE1_MISSING_INPUT_SCHEMA"
    GATE1_MISSING_OUTPUT_SCHEMA = "GATE1_MISSING_OUTPUT_SCHEMA"
    GATE1_MISSING_AGENT_TYPE = "GATE1_MISSING_AGENT_TYPE"
    GATE1_COMPOSITE_REQUIRES_WORKFLOW = "GATE1_COMPOSITE_REQUIRES_WORKFLOW"

    # Gate 2: No Shadow Runtime
    GATE2_SELF_LOOP_DETECTED = "GATE2_SELF_LOOP_DETECTED"
    GATE2_CIRCULAR_DEPENDENCY = "GATE2_CIRCULAR_DEPENDENCY"
    GATE2_UNBOUNDED_ITERATION = "GATE2_UNBOUNDED_ITERATION"

    # Gate 3: Result Sovereignty
    GATE3_MISSING_OUTPUT_NODE = "GATE3_MISSING_OUTPUT_NODE"
    GATE3_EXTERNAL_RESULT_REFERENCE = "GATE3_EXTERNAL_RESULT_REFERENCE"

    # Gate 4: Billing Compliance
    GATE4_BILLING_LOGIC_IN_WORKFLOW = "GATE4_BILLING_LOGIC_IN_WORKFLOW"
    GATE4_DYNAMIC_PRICING_DETECTED = "GATE4_DYNAMIC_PRICING_DETECTED"

    # Gate 5: EIP Dependency Compliance
    GATE5_UNDECLARED_EIP = "GATE5_UNDECLARED_EIP"
    GATE5_INVALID_EIP_VERSION = "GATE5_INVALID_EIP_VERSION"


@dataclass(frozen=True, slots=True)
class GateViolation:
    """
    Represents a single Review Gate violation.

    Attributes:
        gate: Gate number (1-5).
        code: Error code from GateCode enum.
        message: Human-readable description of the violation.
        location: Optional location hint (e.g., "workflow:main", "node:fetch").
    """

    gate: int
    code: GateCode
    message: str
    location: str | None = None


class ReviewGateRules:
    """
    Review Gate validation rules for Agent Definitions.

    Implements the 5 mandatory gates required for Platform Core
    submission. Each method returns a list of violations found.

    IMPORTANT: Passing all gates is necessary but NOT sufficient
    for Platform Core approval. Platform Core performs additional
    governance and security checks.

    Example:
        >>> from ainalyn.domain.rules import ReviewGateRules
        >>> violations = ReviewGateRules.validate_all_gates(agent_definition)
        >>> if violations:
        ...     for v in violations:
        ...         print(f"Gate {v.gate}: {v.message}")
    """

    @staticmethod
    def validate_all_gates(definition: AgentDefinition) -> list[GateViolation]:
        """
        Run all 5 Review Gates and collect violations.

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            list[GateViolation]: All violations found across all gates.
        """
        violations: list[GateViolation] = []
        violations.extend(
            ReviewGateRules.validate_gate1_contract_completeness(definition)
        )
        violations.extend(ReviewGateRules.validate_gate2_no_shadow_runtime(definition))
        violations.extend(ReviewGateRules.validate_gate3_result_sovereignty(definition))
        violations.extend(ReviewGateRules.validate_gate4_billing_compliance(definition))
        violations.extend(ReviewGateRules.validate_gate5_eip_compliance(definition))
        return violations

    @staticmethod
    def validate_gate1_contract_completeness(
        definition: AgentDefinition,
    ) -> list[GateViolation]:
        """
        Gate 1: Contract/External Completeness.

        Validates that the Agent has:
        - Explicit execution goal (task_goal)
        - Determinable completion/failure state (completion_criteria)
        - Complete input/output schema
        - Proper agent_type declaration

        Returns:
            list[GateViolation]: Violations found for Gate 1.
        """
        violations: list[GateViolation] = []

        if not definition.task_goal:
            violations.append(
                GateViolation(
                    gate=1,
                    code=GateCode.GATE1_MISSING_TASK_GOAL,
                    message="Agent must have an explicit task_goal describing what it accomplishes.",
                )
            )

        if not definition.completion_criteria:
            violations.append(
                GateViolation(
                    gate=1,
                    code=GateCode.GATE1_MISSING_COMPLETION_CRITERIA,
                    message="Agent must define completion_criteria with success and failure conditions.",
                )
            )

        if not definition.input_schema:
            violations.append(
                GateViolation(
                    gate=1,
                    code=GateCode.GATE1_MISSING_INPUT_SCHEMA,
                    message="Agent must define input_schema for request validation and UI generation.",
                )
            )

        if not definition.output_schema:
            violations.append(
                GateViolation(
                    gate=1,
                    code=GateCode.GATE1_MISSING_OUTPUT_SCHEMA,
                    message="Agent must define output_schema for result validation.",
                )
            )

        # COMPOSITE agents must have at least one workflow
        from ainalyn.domain.entities.agent_type import AgentType

        if definition.agent_type == AgentType.COMPOSITE and not definition.workflows:
            violations.append(
                GateViolation(
                    gate=1,
                    code=GateCode.GATE1_COMPOSITE_REQUIRES_WORKFLOW,
                    message="COMPOSITE agents must define at least one workflow.",
                )
            )

        return violations

    @staticmethod
    def validate_gate2_no_shadow_runtime(
        definition: AgentDefinition,
    ) -> list[GateViolation]:
        """
        Gate 2: No Shadow Runtime.

        Validates that the Agent does NOT contain:
        - Autonomous loops (self-referencing nodes)
        - Circular dependencies in workflow
        - Persistent memory patterns
        - Self-planning or self-scheduling logic

        Returns:
            list[GateViolation]: Violations found for Gate 2.
        """
        violations: list[GateViolation] = []

        from ainalyn.domain.rules.definition_rules import DefinitionRules

        for workflow in definition.workflows:
            forbidden_keywords = {
                "loop",
                "retry",
                "autonomous",
                "memory",
                "plan",
                "schedule",
                "executionid",
                "pricing",
                "usage",
            }

            # Check for self-loops (node references itself)
            for node in workflow.nodes:
                if node.name in node.next_nodes:
                    violations.append(
                        GateViolation(
                            gate=2,
                            code=GateCode.GATE2_SELF_LOOP_DETECTED,
                            message=f"Node '{node.name}' references itself, creating an autonomous loop.",
                            location=f"workflow:{workflow.name}/node:{node.name}",
                        )
                    )

                node_text = f"{node.name} {node.description} {node.reference}".lower()
                if any(keyword in node_text for keyword in forbidden_keywords):
                    violations.append(
                        GateViolation(
                            gate=2,
                            code=GateCode.GATE2_UNBOUNDED_ITERATION,
                            message=(
                                f"Node '{node.name}' suggests forbidden runtime behavior "
                                "(loops/retries/persistent memory/self-planning/billing)."
                            ),
                            location=f"workflow:{workflow.name}/node:{node.name}",
                        )
                    )

            # Check for circular dependencies
            cycles = DefinitionRules.detect_circular_dependencies(workflow)
            for cycle in cycles:
                cycle_str = " -> ".join(cycle)
                violations.append(
                    GateViolation(
                        gate=2,
                        code=GateCode.GATE2_CIRCULAR_DEPENDENCY,
                        message=f"Circular dependency detected: {cycle_str}",
                        location=f"workflow:{workflow.name}",
                    )
                )

        return violations

    @staticmethod
    def validate_gate3_result_sovereignty(
        definition: AgentDefinition,
    ) -> list[GateViolation]:
        """
        Gate 3: Result Sovereignty.

        Validates that:
        - Output must come from defined workflow
        - No external runtime callbacks that modify results
        - Result is determinable from workflow execution

        For ATOMIC agents, this is delegated to SDK Runtime.
        For COMPOSITE agents, workflows must produce determinable output.

        Returns:
            list[GateViolation]: Violations found for Gate 3.
        """
        violations: list[GateViolation] = []

        from ainalyn.domain.entities.agent_type import AgentType

        # ATOMIC agents delegate result production to SDK Runtime
        if definition.agent_type == AgentType.ATOMIC:
            return violations

        # COMPOSITE agents must have at least one terminal node that produces output
        for workflow in definition.workflows:
            # Find terminal nodes (no outgoing edges)
            terminal_nodes = [node for node in workflow.nodes if not node.next_nodes]

            if not terminal_nodes:
                # All nodes have outgoing edges - possible infinite workflow
                violations.append(
                    GateViolation(
                        gate=3,
                        code=GateCode.GATE3_MISSING_OUTPUT_NODE,
                        message=f"Workflow '{workflow.name}' has no terminal node to produce output.",
                        location=f"workflow:{workflow.name}",
                    )
                )

        return violations

    @staticmethod
    def validate_gate4_billing_compliance(
        definition: AgentDefinition,
    ) -> list[GateViolation]:
        """
        Gate 4: Billing Compliance.

        Validates that:
        - Pricing strategy is descriptive only (hint)
        - No billing calculation logic in workflow
        - No dynamic pricing based on execution

        According to v0.2 specification:
        - Allowed: Declare resource types, provide cost hints
        - Forbidden: Return fees, calculate prices, influence billing

        Returns:
            list[GateViolation]: Violations found for Gate 4.
        """
        violations: list[GateViolation] = []

        # SDK doesn't have execution logic, so Gate 4 violations
        # would primarily come from workflow patterns that suggest
        # dynamic pricing. This is a structural check.

        # Check for suspicious node names that might indicate billing logic
        billing_keywords = {"billing", "price", "cost", "fee", "charge", "invoice"}

        for workflow in definition.workflows:
            for node in workflow.nodes:
                node_name_lower = node.name.lower()
                if any(keyword in node_name_lower for keyword in billing_keywords):
                    violations.append(
                        GateViolation(
                            gate=4,
                            code=GateCode.GATE4_BILLING_LOGIC_IN_WORKFLOW,
                            message=f"Node '{node.name}' appears to involve billing logic. Billing is handled by Platform Core only.",
                            location=f"workflow:{workflow.name}/node:{node.name}",
                        )
                    )

        return violations

    @staticmethod
    def validate_gate5_eip_compliance(
        definition: AgentDefinition,
    ) -> list[GateViolation]:
        """
        Gate 5: EIP Dependency Compliance.

        Validates that:
        - All EIP references in modules/tools are declared in eip_dependencies
        - EIP version constraints are valid
        - Required EIPs are properly declared

        Returns:
            list[GateViolation]: Violations found for Gate 5.
        """
        violations: list[GateViolation] = []

        # Build set of declared EIP dependencies
        declared_eips: set[tuple[str, str]] = set()
        for dep in definition.eip_dependencies:
            declared_eips.add((dep.provider, dep.service))
            if dep.version != "*":
                from ainalyn.domain.rules.definition_rules import DefinitionRules

                if not DefinitionRules.is_valid_version(dep.version):
                    violations.append(
                        GateViolation(
                            gate=5,
                            code=GateCode.GATE5_INVALID_EIP_VERSION,
                            message=(
                                f"EIP dependency '{dep.provider}/{dep.service}' "
                                f"has invalid version '{dep.version}'."
                            ),
                            location=f"eip:{dep.provider}/{dep.service}",
                        )
                    )

        # Check module EIP bindings
        for module in definition.modules:
            if hasattr(module, "eip_binding") and module.eip_binding:
                key = (module.eip_binding.provider, module.eip_binding.service)
                if key not in declared_eips:
                    violations.append(
                        GateViolation(
                            gate=5,
                            code=GateCode.GATE5_UNDECLARED_EIP,
                            message=f"Module '{module.name}' uses EIP '{key[0]}/{key[1]}' which is not declared in eip_dependencies.",
                            location=f"module:{module.name}",
                        )
                    )

        # Check tool EIP bindings
        for tool in definition.tools:
            if hasattr(tool, "eip_binding") and tool.eip_binding:
                key = (tool.eip_binding.provider, tool.eip_binding.service)
                if key not in declared_eips:
                    violations.append(
                        GateViolation(
                            gate=5,
                            code=GateCode.GATE5_UNDECLARED_EIP,
                            message=f"Tool '{tool.name}' uses EIP '{key[0]}/{key[1]}' which is not declared in eip_dependencies.",
                            location=f"tool:{tool.name}",
                        )
                    )

        return violations

    @staticmethod
    def is_gate_passed(violations: list[GateViolation], gate: int) -> bool:
        """
        Check if a specific gate passed (no violations).

        Args:
            violations: List of all violations found.
            gate: Gate number to check (1-5).

        Returns:
            bool: True if the gate has no violations.
        """
        return not any(v.gate == gate for v in violations)

    @staticmethod
    def all_gates_passed(violations: list[GateViolation]) -> bool:
        """
        Check if all gates passed.

        Args:
            violations: List of all violations found.

        Returns:
            bool: True if there are no violations.
        """
        return len(violations) == 0
