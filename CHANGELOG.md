# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-alpha.2] - 2025-12-31

### Added
- **Agent Submission API**: New `submit_agent()` function for direct submission to Platform Core
  - Validates definition before submission
  - Supports custom base_url for staging/testing environments
  - Supports auto_deploy option for automatic deployment after approval
  - Returns `SubmissionResult` with review_id and tracking_url
- **Submission Tracking**: New `track_submission()` function to monitor review status
  - Retrieves current review status from Platform Core
  - Returns feedback from Platform Core's review process
  - Shows agent_id and marketplace_url when approved
- **Domain Entities for Submission**:
  - `SubmissionResult`: Immutable entity representing submission outcome
  - `SubmissionStatus`: Enum for submission lifecycle states (PENDING_REVIEW, ACCEPTED, REJECTED, DRAFT)
  - `ReviewFeedback`: Value object for Platform Core feedback
  - `FeedbackCategory`: Categorizes feedback (SECURITY, COMPLIANCE, QUALITY, etc.)
  - `FeedbackSeverity`: Severity levels (ERROR, WARNING, INFO)
- **Platform Client Adapters**:
  - `HttpPlatformClient`: Placeholder for future Platform Core API integration
  - `MockPlatformClient`: Fully functional mock for testing and development
  - Includes special test cases for authentication errors, network errors, and rejections
- **Use Cases**:
  - `SubmitDefinitionUseCase`: Orchestrates validation, export, and submission workflow
  - `TrackSubmissionUseCase`: Retrieves submission status from Platform Core
- **Error Handling**:
  - `SubmissionError`: Base error for submission failures
  - `AuthenticationError`: Invalid or expired API key
  - `NetworkError`: Network connectivity issues
- **Examples**: New `examples/submit_agent_example.py` demonstrating end-to-end submission workflow

### Changed
- Updated `DefinitionService` to include `submit()` and `track_submission()` methods
- Enhanced `service_factory` to inject `MockPlatformClient` by default
- Updated package exports in `__init__.py` to include submission-related APIs
- Updated README.md with submission workflow documentation

### Documentation
- Added "Submitting Agents to Platform" section to README
- Added comprehensive docstrings for all submission-related APIs
- Included Platform Constitution compliance notes in all submission documentation
- Created detailed implementation plan (IMPLEMENTATION_PLAN_v0.1.0-alpha.2.md)

### Platform Constitution Compliance
- SDK can submit but NOT approve (Platform Core has final authority)
- Submission does NOT create an Execution
- Submission does NOT incur billing (unless platform policy explicitly states)
- All submission workflows respect platform governance boundaries

### Notes
- Currently uses `MockPlatformClient` for testing until Platform Core API is available
- Real HTTP communication will be enabled when Platform Core API endpoints are ready
- This is an alpha release - API may change based on Platform Core requirements

## [0.1.0-alpha.1] - 2024-12-30

### Added
- Initial alpha release of Ainalyn SDK
- Agent Definition builders (`AgentBuilder`, `WorkflowBuilder`, `NodeBuilder`, etc.)
- Fluent API for defining task-oriented agents
- Validation system (`SchemaValidator`, `StaticAnalyzer`)
- YAML export functionality for agent definitions
- CLI tool (`ainalyn` command) for validation and export
- Full type hints support (PEP 561)
- Hexagonal architecture with clean separation of concerns

### Notes
- This is an alpha release for early adopters and testing
- API may change in future versions based on feedback
