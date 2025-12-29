"""
Schema validator for Agent Definitions.

This module implements schema validation as an outbound adapter,
checking structural correctness of AgentDefinition entities.
It implements the IDefinitionSchemaValidator port interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.application.ports.inbound.validate_agent_definition import (
    Severity,
    ValidationError,
)
from ainalyn.domain.rules import DefinitionRules

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition


class SchemaValidator:
    """
    Schema validator for AgentDefinition entities.

    This class implements the IDefinitionSchemaValidator outbound port,
    performing structural and type validation of Agent Definitions.

    ⚠️ SDK BOUNDARY WARNING ⚠️
    This validation checks SDK-level structural correctness only.
    Platform Core applies additional validation during submission.

    The validator checks:
    - Required fields are present and non-empty
    - Naming conventions are followed
    - Version format is correct
    - Workflow and node structures are valid
    - References are defined

    Example:
        >>> from ainalyn.adapters.outbound.schema_validator import SchemaValidator
        >>> from ainalyn.domain.entities import AgentDefinition
        >>> validator = SchemaValidator()
        >>> errors = validator.validate_schema(agent_definition)
        >>> if errors:
        ...     for error in errors:
        ...         print(f"{error.code}: {error.message}")
    """

    def validate_schema(
        self, definition: AgentDefinition
    ) -> tuple[ValidationError, ...]:
        """
        Validate the schema of an AgentDefinition.

        This method performs comprehensive structural validation including:
        - Agent-level validation (name, version, description, workflows)
        - Workflow-level validation (name, nodes, entry_node)
        - Node-level validation (name, type, reference)
        - Resource-level validation (modules, prompts, tools)

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            tuple[ValidationError, ...]: Tuple of validation errors found.
                Empty tuple indicates the schema is valid.
        """
        errors: list[ValidationError] = []

        # Validate agent-level fields
        errors.extend(self._validate_agent_fields(definition))

        # Validate workflows
        errors.extend(self._validate_workflows(definition))

        # Validate resources
        errors.extend(self._validate_resources(definition))

        return tuple(errors)

    def _validate_agent_fields(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Validate agent-level required fields."""
        errors: list[ValidationError] = []

        # Validate name
        if not definition.name:
            errors.append(
                ValidationError(
                    code="MISSING_AGENT_NAME",
                    path="agent.name",
                    message="Agent name is required",
                    severity=Severity.ERROR,
                )
            )
        elif not DefinitionRules.is_valid_name(definition.name):
            errors.append(
                ValidationError(
                    code="INVALID_AGENT_NAME",
                    path="agent.name",
                    message=(
                        f"Agent name '{definition.name}' is invalid. "
                        "Must start with lowercase letter and contain only "
                        "lowercase letters, numbers, and hyphens"
                    ),
                    severity=Severity.ERROR,
                )
            )

        # Validate version
        if not definition.version:
            errors.append(
                ValidationError(
                    code="MISSING_AGENT_VERSION",
                    path="agent.version",
                    message="Agent version is required",
                    severity=Severity.ERROR,
                )
            )
        elif not DefinitionRules.is_valid_version(definition.version):
            errors.append(
                ValidationError(
                    code="INVALID_AGENT_VERSION",
                    path="agent.version",
                    message=(
                        f"Agent version '{definition.version}' is invalid. "
                        "Must follow semantic versioning (e.g., '1.0.0')"
                    ),
                    severity=Severity.ERROR,
                )
            )

        # Validate description
        if not definition.description:
            errors.append(
                ValidationError(
                    code="MISSING_AGENT_DESCRIPTION",
                    path="agent.description",
                    message="Agent description is required",
                    severity=Severity.ERROR,
                )
            )

        # Validate workflows
        if not definition.workflows:
            errors.append(
                ValidationError(
                    code="MISSING_WORKFLOWS",
                    path="agent.workflows",
                    message="Agent must have at least one workflow",
                    severity=Severity.ERROR,
                )
            )

        return errors

    def _validate_workflows(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Validate workflow-level fields."""
        errors: list[ValidationError] = []

        for idx, workflow in enumerate(definition.workflows):
            base_path = f"agent.workflows[{idx}]"

            # Validate workflow name
            if not workflow.name:
                errors.append(
                    ValidationError(
                        code="MISSING_WORKFLOW_NAME",
                        path=f"{base_path}.name",
                        message="Workflow name is required",
                        severity=Severity.ERROR,
                    )
                )
            elif not DefinitionRules.is_valid_name(workflow.name):
                errors.append(
                    ValidationError(
                        code="INVALID_WORKFLOW_NAME",
                        path=f"{base_path}.name",
                        message=(
                            f"Workflow name '{workflow.name}' is invalid. "
                            "Must start with lowercase letter and contain only "
                            "lowercase letters, numbers, and hyphens"
                        ),
                        severity=Severity.ERROR,
                    )
                )

            # Validate workflow description
            if not workflow.description:
                errors.append(
                    ValidationError(
                        code="MISSING_WORKFLOW_DESCRIPTION",
                        path=f"{base_path}.description",
                        message=f"Workflow '{workflow.name}' description is required",
                        severity=Severity.ERROR,
                    )
                )

            # Validate nodes
            if not workflow.nodes:
                errors.append(
                    ValidationError(
                        code="MISSING_WORKFLOW_NODES",
                        path=f"{base_path}.nodes",
                        message=f"Workflow '{workflow.name}' must have at least one node",
                        severity=Severity.ERROR,
                    )
                )

            # Validate entry_node
            if not workflow.entry_node:
                errors.append(
                    ValidationError(
                        code="MISSING_ENTRY_NODE",
                        path=f"{base_path}.entry_node",
                        message=f"Workflow '{workflow.name}' must specify an entry_node",
                        severity=Severity.ERROR,
                    )
                )
            elif not DefinitionRules.workflow_has_valid_entry(workflow):
                errors.append(
                    ValidationError(
                        code="INVALID_ENTRY_NODE",
                        path=f"{base_path}.entry_node",
                        message=(
                            f"Workflow '{workflow.name}' entry_node "
                            f"'{workflow.entry_node}' does not exist in nodes"
                        ),
                        severity=Severity.ERROR,
                    )
                )

            # Validate nodes
            errors.extend(self._validate_nodes(workflow, idx))

        return errors

    def _validate_nodes(
        self,
        workflow: object,
        workflow_idx: int,
    ) -> list[ValidationError]:
        """Validate node-level fields."""
        from ainalyn.domain.entities import Workflow

        if not isinstance(workflow, Workflow):
            return []

        errors: list[ValidationError] = []
        base_path = f"agent.workflows[{workflow_idx}]"

        for node_idx, node in enumerate(workflow.nodes):
            node_path = f"{base_path}.nodes[{node_idx}]"

            # Validate node name
            if not node.name:
                errors.append(
                    ValidationError(
                        code="MISSING_NODE_NAME",
                        path=f"{node_path}.name",
                        message="Node name is required",
                        severity=Severity.ERROR,
                    )
                )
            elif not DefinitionRules.is_valid_name(node.name):
                errors.append(
                    ValidationError(
                        code="INVALID_NODE_NAME",
                        path=f"{node_path}.name",
                        message=(
                            f"Node name '{node.name}' is invalid. "
                            "Must start with lowercase letter and contain only "
                            "lowercase letters, numbers, and hyphens"
                        ),
                        severity=Severity.ERROR,
                    )
                )

            # Validate node description
            if not node.description:
                errors.append(
                    ValidationError(
                        code="MISSING_NODE_DESCRIPTION",
                        path=f"{node_path}.description",
                        message=f"Node '{node.name}' description is required",
                        severity=Severity.ERROR,
                    )
                )

            # Validate node reference
            if not node.reference:
                errors.append(
                    ValidationError(
                        code="MISSING_NODE_REFERENCE",
                        path=f"{node_path}.reference",
                        message=f"Node '{node.name}' must reference a resource",
                        severity=Severity.ERROR,
                    )
                )

            # Validate next_nodes references
            undefined_refs = DefinitionRules.get_undefined_node_references(workflow)
            for source, target in undefined_refs:
                if source == node.name:
                    errors.append(
                        ValidationError(
                            code="UNDEFINED_NODE_REFERENCE",
                            path=f"{node_path}.next_nodes",
                            message=(
                                f"Node '{node.name}' references undefined node '{target}'"
                            ),
                            severity=Severity.ERROR,
                        )
                    )

        return errors

    def _validate_resources(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Validate resource references."""
        errors: list[ValidationError] = []

        # Validate resource references
        undefined_refs = DefinitionRules.get_undefined_resource_references(definition)

        for node_name, resource_type, reference in undefined_refs:
            # Find the node path
            for wf_idx, workflow in enumerate(definition.workflows):
                for node_idx, node in enumerate(workflow.nodes):
                    if node.name == node_name:
                        path = (
                            f"agent.workflows[{wf_idx}].nodes[{node_idx}].reference"
                        )
                        errors.append(
                            ValidationError(
                                code="UNDEFINED_RESOURCE_REFERENCE",
                                path=path,
                                message=(
                                    f"Node '{node_name}' references undefined "
                                    f"{resource_type} '{reference}'"
                                ),
                                severity=Severity.ERROR,
                            )
                        )
                        break

        # Validate resource names
        errors.extend(self._validate_resource_names(definition))

        return errors

    def _validate_resource_names(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Validate resource name conventions."""
        errors: list[ValidationError] = []

        # Validate each resource type
        errors.extend(self._validate_modules(definition))
        errors.extend(self._validate_prompts(definition))
        errors.extend(self._validate_tools(definition))

        return errors

    def _validate_modules(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Validate module resources."""
        errors: list[ValidationError] = []

        for idx, module in enumerate(definition.modules):
            if not module.name:
                errors.append(
                    ValidationError(
                        code="MISSING_MODULE_NAME",
                        path=f"agent.modules[{idx}].name",
                        message="Module name is required",
                        severity=Severity.ERROR,
                    )
                )
            elif not DefinitionRules.is_valid_name(module.name):
                errors.append(
                    ValidationError(
                        code="INVALID_MODULE_NAME",
                        path=f"agent.modules[{idx}].name",
                        message=f"Module name '{module.name}' is invalid",
                        severity=Severity.ERROR,
                    )
                )

            if not module.description:
                errors.append(
                    ValidationError(
                        code="MISSING_MODULE_DESCRIPTION",
                        path=f"agent.modules[{idx}].description",
                        message=f"Module '{module.name}' description is required",
                        severity=Severity.ERROR,
                    )
                )

        return errors

    def _validate_prompts(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Validate prompt resources."""
        errors: list[ValidationError] = []

        for idx, prompt in enumerate(definition.prompts):
            if not prompt.name:
                errors.append(
                    ValidationError(
                        code="MISSING_PROMPT_NAME",
                        path=f"agent.prompts[{idx}].name",
                        message="Prompt name is required",
                        severity=Severity.ERROR,
                    )
                )
            elif not DefinitionRules.is_valid_name(prompt.name):
                errors.append(
                    ValidationError(
                        code="INVALID_PROMPT_NAME",
                        path=f"agent.prompts[{idx}].name",
                        message=f"Prompt name '{prompt.name}' is invalid",
                        severity=Severity.ERROR,
                    )
                )

            if not prompt.description:
                errors.append(
                    ValidationError(
                        code="MISSING_PROMPT_DESCRIPTION",
                        path=f"agent.prompts[{idx}].description",
                        message=f"Prompt '{prompt.name}' description is required",
                        severity=Severity.ERROR,
                    )
                )

            if not prompt.template:
                errors.append(
                    ValidationError(
                        code="MISSING_PROMPT_TEMPLATE",
                        path=f"agent.prompts[{idx}].template",
                        message=f"Prompt '{prompt.name}' template is required",
                        severity=Severity.ERROR,
                    )
                )

        return errors

    def _validate_tools(
        self,
        definition: AgentDefinition,
    ) -> list[ValidationError]:
        """Validate tool resources."""
        errors: list[ValidationError] = []

        for idx, tool in enumerate(definition.tools):
            if not tool.name:
                errors.append(
                    ValidationError(
                        code="MISSING_TOOL_NAME",
                        path=f"agent.tools[{idx}].name",
                        message="Tool name is required",
                        severity=Severity.ERROR,
                    )
                )
            elif not DefinitionRules.is_valid_name(tool.name):
                errors.append(
                    ValidationError(
                        code="INVALID_TOOL_NAME",
                        path=f"agent.tools[{idx}].name",
                        message=f"Tool name '{tool.name}' is invalid",
                        severity=Severity.ERROR,
                    )
                )

            if not tool.description:
                errors.append(
                    ValidationError(
                        code="MISSING_TOOL_DESCRIPTION",
                        path=f"agent.tools[{idx}].description",
                        message=f"Tool '{tool.name}' description is required",
                        severity=Severity.ERROR,
                    )
                )

        return errors
