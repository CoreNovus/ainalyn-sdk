# Implementation Plan: Agent Submission Feature (v0.1.0-alpha.2)

**Status:** Planning Document
**Target Version:** v0.1.0-alpha.2
**Created:** 2025-12-30
**Author:** Development Team

---

## 1. Executive Summary

### 1.1 Current State

The Ainalyn SDK (v0.1.0-alpha.1) provides:
- ✅ Agent Definition compilation and validation
- ✅ YAML export functionality
- ✅ Builder API for defining agents
- ❌ **Missing: Direct submission to Platform Core**

Developers currently must:
1. Compile agent to YAML using SDK
2. Manually upload YAML through Developer Console (not yet available)
3. Manually track review status

### 1.2 Goal

Implement **automated agent submission workflow** to enable:
```python
from ainalyn import AgentBuilder, submit_agent

agent = AgentBuilder("my-agent").version("1.0.0").build()

# New feature: Direct submission
result = submit_agent(agent, api_key="dev_xxx")
if result.is_accepted:
    print(f"Submitted for review: {result.review_id}")
```

### 1.3 Architectural Compliance

All implementations must comply with:
- **Platform Constitution** (`rule-docs/Platform Vision & System Boundary.md`)
- **Agent Canonical Definition** (`rule-docs/Agent Canonical Definition.md`)
- **Execution Lifecycle & Authority** (`rule-docs/Execution Lifecycle & Authority.md`)

**Key Constraints:**
- SDK can only **submit**, not **approve** (Platform Core has final authority)
- Submission creates **description artifacts**, not executions
- No billing occurs during submission (unless platform policy states otherwise)

---

## 2. Architecture Design

### 2.1 Clean Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│  High-Level API (api.py)                            │
│  - submit_agent()                                   │
│  - track_submission()                               │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│  Application Layer                                  │
│  - SubmitDefinitionUseCase                          │
│  - TrackSubmissionUseCase                           │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│  Domain Layer                                       │
│  - SubmissionResult (new entity)                    │
│  - SubmissionStatus (new value object)              │
│  - ReviewFeedback (new value object)                │
└─────────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│  Adapter Layer (Outbound Ports)                     │
│  - IPlatformClient (protocol)                       │
│  - HttpPlatformClient (implementation)              │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
         [Platform Core API]
```

### 2.2 New Components

#### 2.2.1 Domain Entities

**File:** `ainalyn/domain/entities/submission_result.py`

```python
@dataclass(frozen=True, slots=True)
class SubmissionResult:
    """
    Result of submitting an Agent Definition to Platform Core.

    Per Platform Constitution: SDK can submit but not approve.
    Final acceptance is Platform Core's authority.
    """
    review_id: str                    # Unique review tracking ID
    agent_id: str | None              # Assigned if auto-approved
    status: SubmissionStatus          # PENDING_REVIEW, ACCEPTED, REJECTED
    submitted_at: str                 # ISO 8601 timestamp
    tracking_url: str | None          # URL to track review progress
    feedback: tuple[ReviewFeedback, ...] = ()

    @property
    def is_accepted(self) -> bool:
        """Check if submission was accepted for review."""
        return self.status in (
            SubmissionStatus.PENDING_REVIEW,
            SubmissionStatus.ACCEPTED
        )
```

**File:** `ainalyn/domain/value_objects/submission_status.py`

```python
class SubmissionStatus(Enum):
    """Status of an Agent Definition submission."""
    PENDING_REVIEW = "pending_review"   # Awaiting platform review
    ACCEPTED = "accepted"                # Approved and live
    REJECTED = "rejected"                # Rejected by platform
    DRAFT = "draft"                      # Saved as draft (not submitted)
```

**File:** `ainalyn/domain/value_objects/review_feedback.py`

```python
@dataclass(frozen=True, slots=True)
class ReviewFeedback:
    """Feedback from Platform Core during review."""
    category: str          # e.g., "security", "compliance", "quality"
    severity: str          # "error", "warning", "info"
    message: str           # Human-readable feedback
    path: str | None = None  # JSON path to specific issue
```

#### 2.2.2 Application Layer

**File:** `ainalyn/application/ports/outbound/platform_submission.py`

```python
class IPlatformClient(Protocol):
    """
    Outbound port for submitting agents to Platform Core.

    This is a secondary port - implementations handle HTTP/API details.
    """
    def submit_agent(
        self,
        definition: AgentDefinition,
        api_key: str,
        options: SubmissionOptions | None = None,
    ) -> SubmissionResult:
        """Submit an agent definition for platform review."""
        ...

    def get_submission_status(
        self,
        review_id: str,
        api_key: str,
    ) -> SubmissionResult:
        """Retrieve current status of a submission."""
        ...
```

**File:** `ainalyn/application/use_cases/submit_definition.py`

```python
class SubmitDefinitionUseCase:
    """
    Use case: Submit an Agent Definition to Platform Core.

    Workflow:
    1. Validate definition (reuse ValidateDefinitionUseCase)
    2. Export to YAML (reuse ExportDefinitionUseCase)
    3. Submit via Platform Client
    4. Return SubmissionResult

    Per Platform Constitution: SDK submits descriptions, not executions.
    Platform Core has final authority over acceptance.
    """
    def __init__(
        self,
        validator: IValidateAgentDefinition,
        exporter: IExportDefinition,
        platform_client: IPlatformClient,
    ):
        self._validator = validator
        self._exporter = exporter
        self._platform_client = platform_client

    def execute(
        self,
        definition: AgentDefinition,
        api_key: str,
        options: SubmissionOptions | None = None,
    ) -> SubmissionResult:
        """Execute the submission workflow."""
        # 1. Validate
        validation_result = self._validator.execute(definition)
        if not validation_result.is_valid:
            raise SubmissionError(
                "Cannot submit invalid definition",
                validation_errors=validation_result.errors
            )

        # 2. Export
        yaml_content = self._exporter.execute(definition)

        # 3. Submit
        return self._platform_client.submit_agent(
            definition,
            api_key,
            options
        )
```

#### 2.2.3 Adapter Layer

**File:** `ainalyn/adapters/outbound/http_platform_client.py`

```python
class HttpPlatformClient:
    """
    HTTP implementation of Platform Client.

    Handles communication with Platform Core API endpoints.
    """
    def __init__(
        self,
        base_url: str = "https://api.ainalyn.io",
        timeout: int = 30,
    ):
        self._base_url = base_url
        self._timeout = timeout

    def submit_agent(
        self,
        definition: AgentDefinition,
        api_key: str,
        options: SubmissionOptions | None = None,
    ) -> SubmissionResult:
        """
        Submit agent to Platform Core via HTTP POST.

        Endpoint: POST /api/v1/agents/submit
        """
        # Implementation will use requests or httpx
        ...

    def get_submission_status(
        self,
        review_id: str,
        api_key: str,
    ) -> SubmissionResult:
        """
        Get submission status via HTTP GET.

        Endpoint: GET /api/v1/submissions/{review_id}
        """
        ...
```

**Note:** Initial implementation will use **mock responses** until Platform Core API is available.

#### 2.2.4 High-Level API

**File:** `ainalyn/api.py` (additions)

```python
def submit_agent(
    definition: AgentDefinition,
    api_key: str,
    *,
    base_url: str | None = None,
    auto_deploy: bool = False,
) -> SubmissionResult:
    """
    Submit an Agent Definition to Platform Core for review.

    This function:
    1. Validates the definition
    2. Exports to YAML
    3. Submits to Platform Core API

    Important:
    - SDK can submit but NOT approve (Platform Core has final authority)
    - Submission does NOT create an Execution
    - Submission does NOT incur billing (unless platform policy states)

    Args:
        definition: The AgentDefinition to submit.
        api_key: Developer API key for authentication.
        base_url: Optional Platform Core API base URL.
            Defaults to production: https://api.ainalyn.io
        auto_deploy: If True, automatically deploy after approval.
            Requires appropriate permissions.

    Returns:
        SubmissionResult: Contains review_id, status, and tracking URL.

    Raises:
        SubmissionError: If submission fails due to validation or network.
        AuthenticationError: If api_key is invalid.

    Example:
        >>> from ainalyn import AgentBuilder, submit_agent
        >>> agent = AgentBuilder("my-agent").version("1.0.0").build()
        >>> result = submit_agent(agent, api_key="dev_xxx")
        >>> if result.is_accepted:
        ...     print(f"Review ID: {result.review_id}")
        ...     print(f"Track at: {result.tracking_url}")
    """
    service = _get_service()
    return service.submit(
        definition,
        api_key,
        base_url=base_url,
        auto_deploy=auto_deploy
    )


def track_submission(
    review_id: str,
    api_key: str,
    *,
    base_url: str | None = None,
) -> SubmissionResult:
    """
    Track the status of a submitted Agent Definition.

    Args:
        review_id: The review ID returned from submit_agent().
        api_key: Developer API key for authentication.
        base_url: Optional Platform Core API base URL.

    Returns:
        SubmissionResult: Current status and feedback.

    Example:
        >>> result = track_submission("review_abc123", api_key="dev_xxx")
        >>> print(f"Status: {result.status.value}")
        >>> for feedback in result.feedback:
        ...     print(f"- {feedback.message}")
    """
    service = _get_service()
    return service.track_submission(review_id, api_key, base_url=base_url)
```

---

## 3. Implementation Phases

### Phase 1: Domain Layer (Day 1)

**Tasks:**
1. Create `ainalyn/domain/entities/submission_result.py`
2. Create `ainalyn/domain/value_objects/submission_status.py`
3. Create `ainalyn/domain/value_objects/review_feedback.py`
4. Create `ainalyn/domain/errors.py` additions for `SubmissionError`

**Acceptance Criteria:**
- All domain entities are immutable (frozen dataclasses)
- Type hints are complete
- Docstrings reference Platform Constitution

### Phase 2: Application Layer (Day 1-2)

**Tasks:**
1. Create `ainalyn/application/ports/outbound/platform_submission.py`
2. Create `ainalyn/application/use_cases/submit_definition.py`
3. Create `ainalyn/application/use_cases/track_submission.py`
4. Update `ainalyn/application/services/definition_service.py`

**Acceptance Criteria:**
- Use cases depend only on ports (not implementations)
- Validation is performed before submission
- Errors are properly typed and documented

### Phase 3: Adapter Layer (Day 2)

**Tasks:**
1. Create `ainalyn/adapters/outbound/http_platform_client.py`
2. Implement mock responses for testing (until Platform Core is ready)
3. Add configuration for API base URL

**Acceptance Criteria:**
- Client implements `IPlatformClient` protocol
- Network errors are handled gracefully
- Timeout and retry logic is configurable

### Phase 4: High-Level API Integration (Day 2-3)

**Tasks:**
1. Update `ainalyn/api.py` with `submit_agent()` and `track_submission()`
2. Update `ainalyn/__init__.py` exports
3. Update `ainalyn/infrastructure/service_factory.py`

**Acceptance Criteria:**
- API is consistent with existing `validate()` and `compile_agent()`
- Error messages are developer-friendly
- Platform Constitution warnings are included in docstrings

### Phase 5: Testing (Day 3)

**Tasks:**
1. Unit tests for domain entities
2. Unit tests for use cases (with mock platform client)
3. Integration tests for API functions
4. Update existing tests if needed

**Acceptance Criteria:**
- Test coverage > 90% for new code
- Mock responses simulate Platform Core behavior
- Error cases are tested (network failure, auth failure, etc.)

### Phase 6: Examples & Documentation (Day 3-4)

**Tasks:**
1. Create `examples/submit_agent_example.py`
2. Update `examples/price_monitor_agent.py` to show submission
3. Update README.md
4. Create CHANGELOG.md entry for v0.1.0-alpha.2

**Acceptance Criteria:**
- Examples run without errors (using mock client)
- README shows new submission workflow
- CHANGELOG follows Keep a Changelog format

### Phase 7: Version Bump & Release (Day 4)

**Tasks:**
1. Update `ainalyn/_version.py` to `v0.1.0-alpha.2`
2. Update `pyproject.toml` version
3. Run full test suite
4. Tag git commit

**Acceptance Criteria:**
- All tests pass
- Version is consistent across files
- Git tag matches version

---

## 4. API Design Examples

### 4.1 Basic Submission

```python
from ainalyn import AgentBuilder, submit_agent

agent = (
    AgentBuilder("price-monitor")
    .version("1.0.0")
    .description("Monitors prices and notifies users")
    .build()
)

result = submit_agent(agent, api_key="dev_sk_abc123")

if result.is_accepted:
    print(f"✅ Submitted for review")
    print(f"   Review ID: {result.review_id}")
    print(f"   Track at: {result.tracking_url}")
else:
    print(f"❌ Submission rejected")
    for feedback in result.feedback:
        print(f"   - {feedback.message}")
```

### 4.2 Track Submission Status

```python
from ainalyn import track_submission

result = track_submission(
    review_id="review_abc123",
    api_key="dev_sk_abc123"
)

print(f"Status: {result.status.value}")

if result.status == SubmissionStatus.ACCEPTED:
    print(f"🎉 Agent is live: {result.agent_id}")
elif result.status == SubmissionStatus.REJECTED:
    print("❌ Rejected. Feedback:")
    for feedback in result.feedback:
        print(f"   [{feedback.severity}] {feedback.message}")
```

### 4.3 Environment-Specific Submission

```python
from ainalyn import submit_agent

# Submit to staging environment
result = submit_agent(
    agent,
    api_key="dev_sk_staging_xyz",
    base_url="https://staging-api.ainalyn.io"
)
```

### 4.4 Error Handling

```python
from ainalyn import submit_agent, SubmissionError, AuthenticationError

try:
    result = submit_agent(agent, api_key="dev_sk_abc123")
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except SubmissionError as e:
    print(f"Submission failed: {e}")
    if e.validation_errors:
        for error in e.validation_errors:
            print(f"  - {error.code}: {error.message}")
```

---

## 5. Platform Core API Contract (Assumed)

**Note:** This is the **expected** API contract. Actual implementation will be adjusted when Platform Core API is available.

### 5.1 Submit Agent

**Endpoint:** `POST /api/v1/agents/submit`

**Request:**
```json
{
  "definition": {
    "name": "price-monitor",
    "version": "1.0.0",
    "description": "...",
    "workflows": [...],
    "modules": [...],
    "prompts": [...],
    "tools": [...]
  },
  "options": {
    "auto_deploy": false,
    "environment": "production"
  }
}
```

**Headers:**
```
Authorization: Bearer dev_sk_abc123
Content-Type: application/json
```

**Response (202 Accepted):**
```json
{
  "review_id": "review_abc123",
  "status": "pending_review",
  "submitted_at": "2025-12-30T10:00:00Z",
  "tracking_url": "https://console.ainalyn.io/reviews/review_abc123",
  "estimated_review_time": "24h"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "validation_failed",
  "message": "Agent definition failed platform validation",
  "feedback": [
    {
      "category": "security",
      "severity": "error",
      "message": "Tool 'file-writer' requires explicit permission",
      "path": "tools[0]"
    }
  ]
}
```

### 5.2 Get Submission Status

**Endpoint:** `GET /api/v1/submissions/{review_id}`

**Response (200 OK):**
```json
{
  "review_id": "review_abc123",
  "agent_id": "agent_xyz789",
  "status": "accepted",
  "submitted_at": "2025-12-30T10:00:00Z",
  "reviewed_at": "2025-12-30T12:30:00Z",
  "tracking_url": "https://console.ainalyn.io/reviews/review_abc123",
  "marketplace_url": "https://marketplace.ainalyn.io/agents/agent_xyz789",
  "feedback": [
    {
      "category": "quality",
      "severity": "info",
      "message": "Consider adding more detailed description for better discoverability"
    }
  ]
}
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**File:** `tests/unit/domain/entities/test_submission_result.py`
- Test `SubmissionResult` creation
- Test `is_accepted` property logic
- Test immutability

**File:** `tests/unit/application/use_cases/test_submit_definition.py`
- Test submission workflow with mock platform client
- Test validation failure prevents submission
- Test error handling

### 6.2 Integration Tests

**File:** `tests/integration/test_submit_agent_api.py`
- Test `submit_agent()` with mock HTTP responses
- Test `track_submission()` with mock HTTP responses
- Test network error handling

### 6.3 Mock Platform Client

**File:** `tests/mocks/mock_platform_client.py`
```python
class MockPlatformClient:
    """Mock implementation for testing."""
    def submit_agent(self, definition, api_key, options=None):
        if api_key == "invalid":
            raise AuthenticationError("Invalid API key")

        return SubmissionResult(
            review_id="review_mock_123",
            agent_id=None,
            status=SubmissionStatus.PENDING_REVIEW,
            submitted_at="2025-12-30T10:00:00Z",
            tracking_url="https://console.ainalyn.io/reviews/review_mock_123"
        )
```

---

## 7. Documentation Updates

### 7.1 README.md

Add section:
```markdown
### Submitting Agents to Platform

After compiling your agent, submit it directly to the Ainalyn Platform:

```python
from ainalyn import submit_agent

result = submit_agent(agent, api_key="your_api_key")
print(f"Review ID: {result.review_id}")
```

Track submission status:
```python
from ainalyn import track_submission

status = track_submission(result.review_id, api_key="your_api_key")
print(f"Status: {status.status.value}")
```
```

### 7.2 CHANGELOG.md

```markdown
## [0.1.0-alpha.2] - 2025-12-30

### Added
- **Agent Submission API**: New `submit_agent()` function for direct submission to Platform Core
- **Submission Tracking**: New `track_submission()` function to monitor review status
- **Domain Entities**: `SubmissionResult`, `SubmissionStatus`, `ReviewFeedback`
- **Platform Client**: HTTP client adapter for Platform Core API communication
- **Examples**: New `examples/submit_agent_example.py` demonstrating submission workflow

### Changed
- Updated `DefinitionService` to include submission capabilities
- Enhanced API surface in `ainalyn/__init__.py`

### Documentation
- Added submission workflow documentation to README
- Updated examples to show end-to-end workflow
```

---

## 8. Risk Assessment & Mitigation

### 8.1 Platform Core API Availability

**Risk:** Platform Core API endpoints may not be available during alpha phase.

**Mitigation:**
- Implement mock client for testing and examples
- Design adapter pattern to easily swap mock → real implementation
- Document expected API contract for backend team

### 8.2 API Key Management

**Risk:** Developers may hardcode API keys in examples.

**Mitigation:**
- Examples show environment variable usage: `os.getenv("AINALYN_API_KEY")`
- Add warning in documentation about key security
- Consider adding `~/.ainalyn/credentials` config file support

### 8.3 Breaking Changes in Future Versions

**Risk:** Submission API may change as Platform Core evolves.

**Mitigation:**
- Use `alpha` version tag to signal instability
- Document API contract assumptions
- Design for extensibility (use `SubmissionOptions` dataclass)

---

## 9. Success Criteria

### 9.1 Functional Requirements

- ✅ Developers can submit agents via SDK
- ✅ Developers can track submission status
- ✅ Validation errors prevent submission
- ✅ Network errors are handled gracefully
- ✅ API follows Platform Constitution constraints

### 9.2 Non-Functional Requirements

- ✅ Code coverage > 90% for new modules
- ✅ API is consistent with existing SDK style
- ✅ Documentation is complete and accurate
- ✅ Examples run without errors (using mock)
- ✅ Type hints pass mypy strict mode

### 9.3 Release Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Examples run successfully
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped to v0.1.0-alpha.2
- [ ] Git tag created
- [ ] PyPI package published (optional for alpha)

---

## 10. Timeline

**Total Estimated Time:** 3-4 days

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Domain Layer | 4 hours | None |
| Phase 2: Application Layer | 6 hours | Phase 1 |
| Phase 3: Adapter Layer | 4 hours | Phase 2 |
| Phase 4: API Integration | 4 hours | Phase 3 |
| Phase 5: Testing | 8 hours | Phase 4 |
| Phase 6: Examples & Docs | 4 hours | Phase 5 |
| Phase 7: Release | 2 hours | Phase 6 |

**Total:** ~32 hours (~4 working days)

---

## 11. Future Enhancements (Post v0.1.0-alpha.2)

### v0.1.0-alpha.3+
- CLI tool: `ainalyn submit my_agent.yaml`
- Credentials management: `~/.ainalyn/config`
- Batch submission support
- Submission templates
- Interactive submission wizard

### v0.1.0-beta.1+
- Real-time submission status updates (WebSocket)
- Rollback to previous version
- A/B testing support
- Analytics integration

---

## 12. References

- [Platform Constitution](rule-docs/Platform%20Vision%20%26%20System%20Boundary.md)
- [Agent Canonical Definition](rule-docs/Agent%20Canonical%20Definition%20(Marketplace%20Contract%20Entity).md)
- [Execution Lifecycle & Authority](rule-docs/Execution%20Lifecycle%20%26%20Authority.md)
- [Current SDK Documentation](https://corenovus.github.io/ainalyn-sdk/)

---

## Appendix A: File Structure

```
ainalyn-sdk/
├── ainalyn/
│   ├── api.py                                    # ✏️ Modified
│   ├── __init__.py                               # ✏️ Modified
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── submission_result.py              # ➕ New
│   │   ├── value_objects/
│   │   │   ├── submission_status.py              # ➕ New
│   │   │   ├── review_feedback.py                # ➕ New
│   │   └── errors.py                             # ✏️ Modified
│   ├── application/
│   │   ├── ports/
│   │   │   └── outbound/
│   │   │       ├── platform_submission.py        # ➕ New
│   │   ├── use_cases/
│   │   │   ├── submit_definition.py              # ➕ New
│   │   │   └── track_submission.py               # ➕ New
│   │   └── services/
│   │       └── definition_service.py             # ✏️ Modified
│   ├── adapters/
│   │   └── outbound/
│   │       ├── http_platform_client.py           # ➕ New
│   │       └── mock_platform_client.py           # ➕ New (for testing)
│   └── infrastructure/
│       └── service_factory.py                    # ✏️ Modified
├── examples/
│   ├── submit_agent_example.py                   # ➕ New
│   └── price_monitor_agent.py                    # ✏️ Modified
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   │   └── entities/
│   │   │       └── test_submission_result.py     # ➕ New
│   │   └── application/
│   │       └── use_cases/
│   │           └── test_submit_definition.py     # ➕ New
│   └── integration/
│       └── test_submit_agent_api.py              # ➕ New
├── CHANGELOG.md                                  # ✏️ Modified
├── README.md                                     # ✏️ Modified
└── IMPLEMENTATION_PLAN_v0.1.0-alpha.2.md         # ➕ This file
```

**Legend:**
- ➕ New file
- ✏️ Modified file

---

**End of Implementation Plan**
