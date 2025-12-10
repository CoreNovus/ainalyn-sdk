# Testing Strategy and Guidelines

> This document defines the SDK's test layering, test types, and quality requirements.

## 1. Overview of Test Layers

### 1.1 Testing Pyramid

```text
                    ┌─────────────┐
                    │  E2E Tests  │  ← Fewest (verify full flows)
                   ┌┴─────────────┴┐
                   │Integration Tests│  ← Moderate (verify component integration)
                  ┌┴─────────────────┴┐
                  │    Unit Tests     │  ← Most (verify unit behavior)
                 ┌┴───────────────────┴┐
                 │   Contract Tests    │  ← Verify API contracts
                 └────────────────────┘
```

### 1.2 Test Directory Structure

```text
tests/
├── unit/                          # Unit tests
│   ├── domain/                    # Domain layer tests
│   │   ├── models/
│   │   └── errors/
│   ├── application/               # Application layer tests
│   │   ├── clients/
│   │   └── middleware/
│   └── infrastructure/            # Infrastructure layer tests
│       ├── providers/
│       └── storage/
│
├── integration/                   # Integration tests
│   ├── test_chat_flow.py
│   ├── test_storage_integration.py
│   └── test_middleware_chain.py
│
├── contract/                      # Contract tests
│   ├── test_chat_api_contract.py
│   └── test_translation_api_contract.py
│
├── e2e/                           # End-to-end tests
│   └── test_full_conversation.py
│
├── fixtures/                      # Test data
│   ├── responses/                 # Mock responses
│   ├── requests/                  # Test requests
│   └── conftest.py                # Pytest fixtures
│
└── conftest.py                    # Shared configuration
```

---

## 2. Test Strategy by Layer

### 2.1 Domain Layer Tests

**Focus**: Data structure correctness, invariants

```python
# tests/unit/domain/models/test_message.py

import pytest
from datetime import datetime
from ainalyn.domain.models import Message

class TestMessage:
    """Message data structure tests"""

    def test_create_message_with_required_fields(self):
        """Creating a Message requires only the required fields"""
        message = Message(
            id="msg_123",
            role="user",
            content="Hello",
        )

        assert message.id == "msg_123"
        assert message.role == "user"
        assert message.content == "Hello"
        assert isinstance(message.created_at, datetime)

    def test_message_is_immutable(self):
        """Message should be immutable"""
        message = Message(id="1", role="user", content="test")

        with pytest.raises(AttributeError):
            message.content = "modified"  # type: ignore

    def test_message_equality(self):
        """Messages with the same content should be equal"""
        msg1 = Message(id="1", role="user", content="Hello")
        msg2 = Message(id="1", role="user", content="Hello")

        assert msg1 == msg2

    @pytest.mark.parametrize("role", ["user", "assistant", "system"])
    def test_valid_message_roles(self, role: str):
        """Message supports all valid roles"""
        message = Message(id="1", role=role, content="test")
        assert message.role == role
```

### 2.2 Application Layer Tests

**Focus**: Flow correctness, order of Port calls

```python
# tests/unit/application/clients/test_chat_client.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from ainalyn.application.clients import ChatClient
from ainalyn.domain.models import Message, Session
from ainalyn.domain.ports import ProviderPort, StoragePort

class TestChatClient:
    """ChatClient unit tests"""

    @pytest.fixture
    def mock_provider(self) -> AsyncMock:
        provider = AsyncMock(spec=ProviderPort)
        provider.send_request.return_value = ProviderResponse(
            content="Hello!",
            usage=Usage(input_tokens=5, output_tokens=2),
        )
        return provider

    @pytest.fixture
    def mock_storage(self) -> AsyncMock:
        storage = AsyncMock(spec=StoragePort)
        storage.save_session.return_value = "sess_123"
        storage.get_session.return_value = None
        return storage

    @pytest.fixture
    def client(
        self,
        mock_provider: AsyncMock,
        mock_storage: AsyncMock,
    ) -> ChatClient:
        return ChatClient(
            provider=mock_provider,
            storage=mock_storage,
        )

    async def test_send_message_creates_new_session(
        self,
        client: ChatClient,
        mock_storage: AsyncMock,
    ):
        """Should create a new Session when session_id is not provided"""
        response = await client.send_message("Hello")

        mock_storage.save_session.assert_called_once()
        assert response.session_id == "sess_123"

    async def test_send_message_uses_existing_session(
        self,
        client: ChatClient,
        mock_storage: AsyncMock,
    ):
        """Should use existing Session when session_id is provided"""
        existing_session = Session(id="sess_existing", messages=[])
        mock_storage.get_session.return_value = existing_session

        response = await client.send_message(
            "Hello",
            session_id="sess_existing",
        )

        mock_storage.get_session.assert_called_once_with("sess_existing")
        assert response.session_id == "sess_existing"

    async def test_send_message_calls_provider(
        self,
        client: ChatClient,
        mock_provider: AsyncMock,
    ):
        """Should call Provider to send request"""
        await client.send_message("Hello")

        mock_provider.send_request.assert_called_once()
        request = mock_provider.send_request.call_args[0][0]
        assert "Hello" in request.messages[-1].content

    async def test_send_message_saves_messages(
        self,
        client: ChatClient,
        mock_storage: AsyncMock,
    ):
        """Should store both user and assistant messages"""
        await client.send_message("Hello")

        # Verify that two messages were saved (user + assistant)
        save_calls = mock_storage.save_message.call_args_list
        assert len(save_calls) == 2
        assert save_calls[0][0][1].role == "user"
        assert save_calls[1][0][1].role == "assistant"
```

### 2.3 Infrastructure Layer Tests

**Focus**: External integration correctness, error handling

```python
# tests/unit/infrastructure/providers/test_http_provider.py

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from ainalyn.infrastructure.providers import HttpProvider
from ainalyn.domain.errors import (
    AuthenticationError,
    RateLimitError,
    NetworkError,
)

class TestHttpProvider:
    """HttpProvider unit tests"""

    @pytest.fixture
    def provider(self) -> HttpProvider:
        return HttpProvider(
            base_url="https://api.example.com",
            api_key="test-key",
        )

    async def test_send_request_includes_auth_header(
        self,
        provider: HttpProvider,
    ):
        """Request should include auth header"""
        with patch.object(
            provider._client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = httpx.Response(
                200,
                json={"content": "response"},
            )

            await provider.send_request(ProviderRequest(content="test"))

            headers = mock_post.call_args.kwargs.get("headers", {})
            assert "Authorization" in headers
            assert "test-key" in headers["Authorization"]

    async def test_handles_401_as_authentication_error(
        self,
        provider: HttpProvider,
    ):
        """401 response should be converted to AuthenticationError"""
        with patch.object(
            provider._client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = httpx.Response(401, json={"error": "Invalid"})

            with pytest.raises(AuthenticationError) as exc_info:
                await provider.send_request(ProviderRequest(content="test"))

            assert exc_info.value.status_code == 401

    async def test_handles_429_as_rate_limit_error(
        self,
        provider: HttpProvider,
    ):
        """429 response should be converted to RateLimitError"""
        with patch.object(
            provider._client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = httpx.Response(
                429,
                json={"error": "Too many requests"},
                headers={"Retry-After": "60"},
            )

            with pytest.raises(RateLimitError) as exc_info:
                await provider.send_request(ProviderRequest(content="test"))

            assert exc_info.value.retry_after == 60

    async def test_handles_network_error(
        self,
        provider: HttpProvider,
    ):
        """Network errors should be converted to NetworkError"""
        with patch.object(
            provider._client, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(NetworkError):
                await provider.send_request(ProviderRequest(content="test"))
```

---

## 3. Integration Tests

### 3.1 Storage Integration Tests

```python
# tests/integration/test_storage_integration.py

import pytest
from datetime import datetime
from ainalyn.infrastructure.storage import SQLiteStorage
from ainalyn.domain.models import Session, Message

class TestSQLiteStorageIntegration:
    """SQLite Storage integration tests"""

    @pytest.fixture
    async def storage(self, tmp_path):
        """Create test storage"""
        db_path = tmp_path / "test.db"
        storage = SQLiteStorage(str(db_path))
        await storage.initialize()
        yield storage
        await storage.close()

    async def test_session_crud_operations(self, storage: SQLiteStorage):
        """Complete Session CRUD flow"""
        # Create
        session = Session(id="sess_1", messages=[])
        session_id = await storage.save_session(session)
        assert session_id == "sess_1"

        # Read
        retrieved = await storage.get_session(session_id)
        assert retrieved is not None
        assert retrieved.id == session_id

        # Update
        message = Message(id="msg_1", role="user", content="Hello")
        await storage.save_message(session_id, message)

        updated = await storage.get_session(session_id)
        assert updated is not None
        messages = await storage.get_messages(session_id)
        assert len(messages) == 1

        # Delete
        await storage.delete_session(session_id)
        deleted = await storage.get_session(session_id)
        assert deleted is None

    async def test_concurrent_message_saves(self, storage: SQLiteStorage):
        """Concurrent message saves should not conflict"""
        import asyncio

        session = Session(id="sess_concurrent", messages=[])
        await storage.save_session(session)

        # Save 10 messages concurrently
        tasks = [
            storage.save_message(
                "sess_concurrent",
                Message(id=f"msg_{i}", role="user", content=f"Message {i}")
            )
            for i in range(10)
        ]
        await asyncio.gather(*tasks)

        messages = await storage.get_messages("sess_concurrent")
        assert len(messages) == 10
```

### 3.2 Middleware Chain Integration Tests

```python
# tests/integration/test_middleware_chain.py

import pytest
from ainalyn.application.middleware import MiddlewareChain
from ainalyn.infrastructure.middleware import (
    LoggingMiddleware,
    RetryMiddleware,
)

class TestMiddlewareChainIntegration:
    """Middleware Chain integration tests"""

    async def test_middleware_execution_order(self):
        """Middleware should execute in the correct order"""
        execution_order = []

        class TrackingMiddleware:
            def __init__(self, name: str):
                self.name = name

            async def before_request(self, context):
                execution_order.append(f"{self.name}_before")
                return context

            async def after_request(self, context, response):
                execution_order.append(f"{self.name}_after")
                return response

        chain = MiddlewareChain([
            TrackingMiddleware("first"),
            TrackingMiddleware("second"),
            TrackingMiddleware("third"),
        ])

        # Execute chain
        await chain.execute(mock_context, mock_handler)

        assert execution_order == [
            "first_before",
            "second_before",
            "third_before",
            "third_after",
            "second_after",
            "first_after",
        ]

    async def test_retry_middleware_integration(self):
        """RetryMiddleware integration test"""
        attempt_count = 0

        async def failing_handler(context):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise NetworkError("Connection failed")
            return ProviderResponse(content="Success")

        chain = MiddlewareChain([
            RetryMiddleware(max_attempts=3),
        ])

        response = await chain.execute(mock_context, failing_handler)

        assert attempt_count == 3
        assert response.content == "Success"
```

---

## 4. Contract Tests

### 4.1 API Contract Validation

```python
# tests/contract/test_chat_api_contract.py

import pytest
import yaml
from jsonschema import validate, ValidationError
from pathlib import Path

class TestChatApiContract:
    """Chat API contract tests"""

    @pytest.fixture
    def api_spec(self) -> dict:
        """Load OpenAPI spec"""
        spec_path = Path("contracts/openapi/chat-api.yaml")
        with open(spec_path) as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def send_message_request_schema(self, api_spec: dict) -> dict:
        """Get SendMessage request schema"""
        return api_spec["components"]["schemas"]["SendMessageRequest"]

    @pytest.fixture
    def chat_response_schema(self, api_spec: dict) -> dict:
        """Get Chat response schema"""
        return api_spec["components"]["schemas"]["ChatResponse"]

    def test_request_matches_contract(
        self,
        send_message_request_schema: dict,
    ):
        """SDK request format should conform to the contract"""
        # Request generated by the SDK
        request = {
            "message": "Hello",
            "sessionId": "sess_123",
            "provider": "openai",
            "model": "gpt-4",
            "stream": False,
        }

        # Validate against schema
        validate(instance=request, schema=send_message_request_schema)

    def test_response_parsing_matches_contract(
        self,
        chat_response_schema: dict,
    ):
        """API response format should conform to the contract"""
        # Simulated API response
        response = {
            "success": True,
            "data": {
                "message": {
                    "id": "msg_123",
                    "role": "assistant",
                    "content": "Hello!",
                    "createdAt": "2024-01-01T00:00:00Z",
                },
                "sessionId": "sess_123",
                "usage": {
                    "inputTokens": 5,
                    "outputTokens": 2,
                    "totalTokens": 7,
                },
            },
        }

        validate(instance=response, schema=chat_response_schema)

    def test_invalid_request_rejected(
        self,
        send_message_request_schema: dict,
    ):
        """Invalid request should be rejected"""
        invalid_request = {
            # Missing required message field
            "sessionId": "sess_123",
        }

        with pytest.raises(ValidationError):
            validate(instance=invalid_request, schema=send_message_request_schema)
```

---

## 5. Mock and Fixture Strategy

### 5.1 Shared Fixtures

```python
# tests/fixtures/conftest.py

import pytest
from datetime import datetime
from ainalyn.domain.models import Message, Session

@pytest.fixture
def sample_message() -> Message:
    """Sample message"""
    return Message(
        id="msg_test",
        role="user",
        content="Test message",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )

@pytest.fixture
def sample_session(sample_message: Message) -> Session:
    """Sample session"""
    return Session(
        id="sess_test",
        messages=[sample_message],
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )

@pytest.fixture
def mock_provider_response() -> dict:
    """Mock provider response"""
    return {
        "content": "This is a test response",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
        },
    }
```

### 5.2 Mock API Responses

```python
# tests/fixtures/responses/chat_responses.py

CHAT_SUCCESS_RESPONSE = {
    "success": True,
    "data": {
        "message": {
            "id": "msg_abc123",
            "role": "assistant",
            "content": "Hello! How can I help you today?",
            "createdAt": "2024-01-01T12:00:00Z",
        },
        "sessionId": "sess_xyz789",
        "usage": {
            "inputTokens": 15,
            "outputTokens": 10,
            "totalTokens": 25,
        },
    },
}

CHAT_ERROR_RESPONSE = {
    "success": False,
    "error": "Rate limit exceeded",
    "code": "INF_PRV_RATE_LIMITED",
    "message": "Please wait before making another request",
}

CHAT_STREAM_CHUNKS = [
    {"type": "content", "content": "Hello"},
    {"type": "content", "content": "! How"},
    {"type": "content", "content": " can I"},
    {"type": "content", "content": " help?"},
    {"type": "end", "usage": {"inputTokens": 5, "outputTokens": 4}},
]
```

---

## 6. Test Quality Requirements

### 6.1 Coverage Requirements

| Layer          | Minimum Coverage | Target Coverage |
| -------------- | ---------------- | --------------- |
| Domain         | 95%              | 100%            |
| Application    | 90%              | 95%             |
| Infrastructure | 80%              | 90%             |
| Interface      | 70%              | 80%             |
| Overall        | 85%              | 90%             |

### 6.2 Test Execution Configuration

```toml
# pyproject.toml

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "-ra",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
]

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
fail_under = 85
```

### 6.3 CI Test Workflow

```yaml
# .github/workflows/test.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run unit tests
        run: |
          pytest tests/unit -v --cov=src --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration -v --cov=src --cov-append --cov-report=xml

      - name: Run contract tests
        run: |
          pytest tests/contract -v

      - name: Check coverage
        run: |
          coverage report --fail-under=85

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

---

## 7. Test Checklist

### Must Verify Before Submitting a PR

* [ ] All new code has corresponding unit tests
* [ ] Unit test coverage >= 85%
* [ ] Important flows have integration tests
* [ ] API changes have updated contract tests
* [ ] All tests pass (`pytest`)
* [ ] No flaky tests

### New Feature Test Checklist

* [ ] Happy path tests
* [ ] Boundary condition tests
* [ ] Error handling tests
* [ ] Concurrency/race condition tests (if applicable)
* [ ] Performance tests (if applicable)

---

*Last updated: 2024-12*
