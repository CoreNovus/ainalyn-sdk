"""
Application services for Ainalyn SDK.

This module provides high-level services that encapsulate
use cases and provide a simplified API for SDK consumers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ainalyn.application.use_cases.compile_definition import (
    CompilationResult,
    CompileDefinitionUseCase,
)
from ainalyn.application.use_cases.export_definition import ExportDefinitionUseCase
from ainalyn.application.use_cases.submit_definition import (
    SubmitDefinitionUseCase,
    TrackSubmissionUseCase,
)
from ainalyn.application.use_cases.validate_definition import ValidateDefinitionUseCase

if TYPE_CHECKING:
    from pathlib import Path

    from ainalyn.application.ports.inbound.validate_agent_definition import (
        ValidationResult,
    )
    from ainalyn.application.ports.outbound.definition_persistence import (
        IDefinitionWriter,
    )
    from ainalyn.application.ports.outbound.definition_schema_validation import (
        IDefinitionSchemaValidator,
    )
    from ainalyn.application.ports.outbound.definition_serialization import (
        IDefinitionSerializer,
    )
    from ainalyn.application.ports.outbound.definition_static_analysis import (
        IDefinitionAnalyzer,
    )
    from ainalyn.application.ports.outbound.platform_submission import (
        IPlatformClient,
        SubmissionOptions,
    )
    from ainalyn.domain.entities import AgentDefinition, SubmissionResult


class DefinitionService:
    """
    Unified service for Agent Definition operations.

    This service provides a simplified, high-level API for working with
    Agent Definitions. It encapsulates all use cases and manages their
    dependencies, offering a clean interface for SDK consumers.

    The service supports three main operations:
    1. Validation - Verify structural and logical correctness
    2. Export - Convert to YAML format
    3. Compilation - Complete validate-and-export workflow

    Example:
        >>> from ainalyn.application.services import DefinitionService
        >>> from pathlib import Path
        >>> service = DefinitionService()
        >>> # Validate only
        >>> result = service.validate(agent_definition)
        >>> if result.is_valid:
        ...     print("Valid!")
        >>> # Compile to string
        >>> compilation = service.compile(agent_definition)
        >>> if compilation.is_successful:
        ...     print(compilation.yaml_content)
        >>> # Compile to file
        >>> compilation = service.compile_to_file(
        ...     agent_definition,
        ...     Path("agent.yaml")
        ... )
    """

    def __init__(
        self,
        schema_validator: IDefinitionSchemaValidator,
        static_analyzer: IDefinitionAnalyzer,
        serializer: IDefinitionSerializer,
        writer: IDefinitionWriter | None = None,
        platform_client: IPlatformClient | None = None,
    ) -> None:
        """
        Initialize the definition service with injected dependencies.

        This constructor uses dependency injection to wire the service
        with concrete adapter implementations. The adapters are provided
        through port interfaces, maintaining clean separation between
        application core and adapters.

        Args:
            schema_validator: Port for schema validation capability.
            static_analyzer: Port for static analysis capability.
            serializer: Port for serialization capability (e.g., YAML).
            writer: Optional port for persistence capability (e.g., file writer).
            platform_client: Optional port for Platform Core API communication.
                Required for submission features.

        Example:
            >>> from ainalyn.infrastructure import create_default_service
            >>> service = create_default_service()
            >>> # Or with custom adapters:
            >>> service = DefinitionService(
            ...     schema_validator=MyCustomValidator(),
            ...     static_analyzer=MyCustomAnalyzer(),
            ...     serializer=MyCustomSerializer(),
            ...     platform_client=MyPlatformClient(),
            ... )
        """
        # Store injected adapters
        self._schema_validator = schema_validator
        self._static_analyzer = static_analyzer
        self._serializer = serializer
        self._writer = writer
        self._platform_client = platform_client

        # Initialize use cases with injected dependencies
        self._validate_use_case = ValidateDefinitionUseCase(
            self._schema_validator,
            self._static_analyzer,
        )
        self._export_use_case = ExportDefinitionUseCase(self._serializer)
        self._compile_use_case = CompileDefinitionUseCase(
            self._validate_use_case,
            self._export_use_case,
        )

        # Initialize submission use cases (lazy - only if platform_client provided)
        self._submit_use_case: SubmitDefinitionUseCase | None = None
        self._track_use_case: TrackSubmissionUseCase | None = None
        if self._platform_client:
            self._submit_use_case = SubmitDefinitionUseCase(
                self._validate_use_case,
                self._serializer,
                self._platform_client,
            )
            self._track_use_case = TrackSubmissionUseCase(self._platform_client)

    def validate(self, definition: AgentDefinition) -> ValidationResult:
        """
        Validate an AgentDefinition.

        This method performs comprehensive validation including:
        - Schema validation (structural correctness)
        - Static analysis (logical consistency)

        Args:
            definition: The AgentDefinition to validate.

        Returns:
            ValidationResult: Contains all errors and warnings found.
                Use result.is_valid to check if validation passed.

        Example:
            >>> service = DefinitionService()
            >>> result = service.validate(agent_definition)
            >>> if not result.is_valid:
            ...     for error in result.errors:
            ...         print(f"{error.code}: {error.message}")
        """
        return self._validate_use_case.execute(definition)

    def export(self, definition: AgentDefinition) -> str:
        """
        Export an AgentDefinition to YAML string.

        This method converts the AgentDefinition into a YAML-formatted
        string without performing validation. For safety, use compile()
        instead to ensure validation before export.

        Args:
            definition: The AgentDefinition to export.

        Returns:
            str: The YAML-formatted string representation.

        Raises:
            yaml.YAMLError: If YAML serialization fails.

        Warning:
            This method does not validate the definition before export.
            Use compile() for a safer, validated export workflow.

        Example:
            >>> service = DefinitionService()
            >>> yaml_string = service.export(agent_definition)
            >>> print(yaml_string)
        """
        return self._export_use_case.execute(definition)

    def export_to_file(self, definition: AgentDefinition, path: Path) -> None:
        """
        Export an AgentDefinition to a YAML file.

        This method converts the AgentDefinition to YAML and writes it
        to the specified file path without performing validation.
        For safety, use compile_to_file() instead.

        Args:
            definition: The AgentDefinition to export.
            path: The destination file path.

        Raises:
            yaml.YAMLError: If YAML serialization fails.
            IOError: If the file cannot be written.
            PermissionError: If write permission is denied.

        Warning:
            This method does not validate the definition before export.
            Use compile_to_file() for a safer, validated export workflow.

        Example:
            >>> service = DefinitionService()
            >>> service.export_to_file(agent_definition, Path("agent.yaml"))
        """
        self._export_use_case.execute_to_file(definition, path)

    def compile(self, definition: AgentDefinition) -> CompilationResult:
        """
        Compile an AgentDefinition.

        This method performs the complete compilation workflow:
        1. Validate the definition (schema + static analysis)
        2. Export to YAML (only if validation passes)

        Args:
            definition: The AgentDefinition to compile.

        Returns:
            CompilationResult: Contains validation result and YAML content
                (if validation passed).

        Example:
            >>> service = DefinitionService()
            >>> result = service.compile(agent_definition)
            >>> if result.is_successful:
            ...     print("Compilation successful!")
            ...     print(result.yaml_content)
            ... else:
            ...     print("Validation failed:")
            ...     for error in result.validation_result.errors:
            ...         print(f"  {error.code}: {error.message}")
        """
        return self._compile_use_case.execute(definition)

    def compile_to_file(
        self,
        definition: AgentDefinition,
        output_path: Path,
    ) -> CompilationResult:
        """
        Compile an AgentDefinition and write to file.

        This method performs the complete compilation workflow:
        1. Validate the definition (schema + static analysis)
        2. Export to YAML file (only if validation passes)

        Args:
            definition: The AgentDefinition to compile.
            output_path: The destination file path.

        Returns:
            CompilationResult: Contains validation result, YAML content,
                and output path (if validation passed).

        Raises:
            IOError: If the file cannot be written (only if validation passes).
            PermissionError: If write permission is denied (only if validation passes).

        Example:
            >>> service = DefinitionService()
            >>> result = service.compile_to_file(
            ...     agent_definition,
            ...     Path("agent.yaml")
            ... )
            >>> if result.is_successful:
            ...     print(f"Compiled to {result.output_path}")
            ... else:
            ...     print("Validation failed")
        """
        return self._compile_use_case.execute_to_file(definition, output_path)

    def submit(
        self,
        definition: AgentDefinition,
        api_key: str,
        options: SubmissionOptions | None = None,
    ) -> SubmissionResult:
        """
        Submit an AgentDefinition to Platform Core for review.

        This method performs the complete submission workflow:
        1. Validate the definition (SDK-level validation)
        2. Export to YAML format
        3. Submit to Platform Core API

        Per Platform Constitution:
        - SDK can submit but NOT approve agents
        - Platform Core has final authority over acceptance
        - Submission does NOT create an Execution
        - Submission does NOT incur billing (unless platform policy states)

        Args:
            definition: The AgentDefinition to submit.
            api_key: Developer API key for authentication.
            options: Optional submission configuration.

        Returns:
            SubmissionResult: Result containing review_id, status,
                and tracking information.

        Raises:
            RuntimeError: If platform client was not provided during
                service initialization.
            SubmissionError: If SDK validation fails or submission fails.
            AuthenticationError: If api_key is invalid or expired.
            NetworkError: If network communication with Platform Core fails.

        Example:
            >>> service = DefinitionService(
            ...     ...,
            ...     platform_client=HttpPlatformClient()
            ... )
            >>> result = service.submit(
            ...     definition=agent,
            ...     api_key="dev_sk_abc123",
            ...     options=SubmissionOptions(auto_deploy=True)
            ... )
            >>> print(f"Review ID: {result.review_id}")
            >>> print(f"Track at: {result.tracking_url}")
        """
        if not self._submit_use_case:
            raise RuntimeError(
                "Platform client not configured. "
                "Provide platform_client when initializing DefinitionService "
                "to enable submission features."
            )
        return self._submit_use_case.execute(definition, api_key, options)

    def track_submission(
        self,
        review_id: str,
        api_key: str,
    ) -> SubmissionResult:
        """
        Track the status of a previously submitted agent.

        This method queries Platform Core for the current status
        of a submission.

        Args:
            review_id: The review ID returned from submit().
            api_key: Developer API key for authentication.

        Returns:
            SubmissionResult: Current status, feedback, and if approved,
                the agent_id and marketplace URL.

        Raises:
            RuntimeError: If platform client was not provided during
                service initialization.
            AuthenticationError: If api_key is invalid.
            NetworkError: If network communication fails.
            SubmissionError: If review_id is not found or other errors.

        Example:
            >>> service = DefinitionService(..., platform_client=HttpPlatformClient())
            >>> result = service.track_submission(
            ...     review_id="review_abc123",
            ...     api_key="dev_sk_abc123"
            ... )
            >>> if result.is_live:
            ...     print(f"Agent is live: {result.marketplace_url}")
            >>> elif result.is_rejected:
            ...     for issue in result.get_blocking_issues():
            ...         print(f"[ERROR] {issue.message}")
        """
        if not self._track_use_case:
            raise RuntimeError(
                "Platform client not configured. "
                "Provide platform_client when initializing DefinitionService "
                "to enable submission features."
            )
        return self._track_use_case.execute(review_id, api_key)
