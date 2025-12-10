# Internal Coding Conventions and Standards

> This document defines the coding conventions, naming rules, and best practices for internal SDK development.

## 1. Python Version and Basic Conventions

### 1.1 Version Requirements

* **Minimum Python version**: 3.11
* **Type hints**: Use Python 3.11+ type annotation syntax throughout
* **Async/Await**: All I/O operations must use async

### 1.2 Formatting Tools

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # line too long (black handles this)

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### 1.3 Import Order

```python
# 1. Standard library
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any, Protocol

# 2. Third-party packages
import httpx
from pydantic import BaseModel

# 3. Internal - Domain
from ainalyn.domain.models import Message, Session
from ainalyn.domain.ports import ProviderPort

# 4. Internal - Same layer
from .client import BaseClient
from .middleware import MiddlewareChain
```

---

## 2. Naming Conventions

### 2.1 File Naming

| Type      | Format     | Example               |
| --------- | ---------- | --------------------- |
| Module    | snake_case | `chat_client.py`      |
| Package   | snake_case | `text_to_music/`      |
| Tests     | test_*.py  | `test_chat_client.py` |
| Type defs | *_types.py | `chat_types.py`       |

### 2.2 Class Naming

| Type               | Format     | Example                            |
| ------------------ | ---------- | ---------------------------------- |
| General class      | PascalCase | `ChatClient`                       |
| Protocol/Interface | *Port      | `ProviderPort`, `StoragePort`      |
| Abstract base      | Base*      | `BaseClient`, `BaseProvider`       |
| Mixin              | *Mixin     | `LoggingMixin`                     |
| Exception          | *Error     | `ProviderError`, `ValidationError` |
| Data class         | PascalCase | `ChatMessage`, `TranslationResult` |

### 2.3 Function/Method Naming

| Type       | Format             | Example                               |
| ---------- | ------------------ | ------------------------------------- |
| General    | snake_case         | `send_message()`                      |
| Async      | snake_case         | `async def get_session()`             |
| Private    | _snake_case        | `def _validate_input()`               |
| Factory    | create_*           | `create_client()`, `create_session()` |
| Getter     | get_*              | `get_messages()`, `get_status()`      |
| Setter     | set_*              | `set_config()`                        |
| Boolean    | is_*, has_*, can_* | `is_valid()`, `has_messages()`        |
| Conversion | to_*, from_*       | `to_dict()`, `from_json()`            |

### 2.4 Variable Naming

| Type          | Format                     | Example           |
| ------------- | -------------------------- | ----------------- |
| General       | snake_case                 | `message_count`   |
| Constant      | UPPER_SNAKE_CASE           | `DEFAULT_TIMEOUT` |
| Private       | _snake_case                | `_internal_state` |
| Type variable | T, K, V or meaningful name | `T`, `ResponseT`  |

---

## 3. Type Annotation Conventions

### 3.1 Basic Principles

```python
# Use built-in types in Python 3.11+
def process_items(items: list[str]) -> dict[str, int]:
    ...

# Use | instead of Union
def get_value(key: str) -> str | None:
    ...

# Use special types from typing
from typing import Any, Protocol, TypeVar, Generic
```

### 3.2 Protocol Definition

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProviderPort(Protocol):
    """Provider abstract interface"""

    async def send_request(
        self,
        request: ProviderRequest,
        options: ProviderOptions | None = None,
    ) -> ProviderResponse:
        """Send a request"""
        ...
```

### 3.3 Generic Classes

```python
from typing import Generic, TypeVar

T = TypeVar("T")
ResponseT = TypeVar("ResponseT", bound="BaseResponse")

class ApiResponse(Generic[T]):
    """Generic API response"""

    def __init__(self, data: T, success: bool = True) -> None:
        self.data = data
        self.success = success
```

### 3.4 Callable Annotations

```python
from collections.abc import Callable, Awaitable

# Sync callback
Callback = Callable[[str], None]

# Async callback
AsyncCallback = Callable[[str], Awaitable[None]]

# Complex callback
TokenHandler = Callable[[str, int], Awaitable[bool]]
```

---

## 4. Data Structure Conventions

### 4.1 Domain Models Use dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)  # Immutable
class Message:
    """Chat message"""

    id: str
    role: str  # "user" | "assistant" | "system"
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Conversation session"""

    id: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        self.updated_at = datetime.now()
```

### 4.2 Request/Response Use Pydantic (Interface Layer)

```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Chat API request (public)"""

    message: str = Field(..., min_length=1, max_length=10000)
    session_id: str | None = None
    stream: bool = False
    options: ChatOptions | None = None

    model_config = {
        "extra": "forbid",  # Forbid extra fields
    }
```

### 4.3 Enum Usage

```python
from enum import Enum, auto

class MessageRole(str, Enum):
    """Message role"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class TaskStatus(str, Enum):
    """Task status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## 5. Async Programming Conventions

### 5.1 All I/O Operations Must Be async

```python
# ✅ Correct
async def fetch_data(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ❌ Incorrect - synchronous I/O
def fetch_data(url: str) -> dict[str, Any]:
    response = requests.get(url)
    return response.json()
```

### 5.2 Resource Management with async Context Manager

```python
class DatabaseConnection:
    async def __aenter__(self) -> Self:
        await self._connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._disconnect()
```

### 5.3 Concurrency Control

```python
import asyncio

# Use Semaphore to limit concurrency
async def process_batch(
    items: list[str],
    max_concurrent: int = 10
) -> list[Result]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_limit(item: str) -> Result:
        async with semaphore:
            return await process_item(item)

    return await asyncio.gather(
        *[process_with_limit(item) for item in items]
    )
```

### 5.4 Cancellation Handling

```python
async def long_running_task() -> Result:
    try:
        while True:
            await asyncio.sleep(1)
            # Periodically check for cancellation
            if some_condition:
                break
    except asyncio.CancelledError:
        # Clean up resources
        await cleanup()
        raise  # Re-raise
```

---

## 6. Error Handling Conventions

### 6.1 Custom Exception Hierarchy

```python
# Base exception
class AinalynError(Exception):
    """Base SDK exception"""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


# Domain-layer exception
class ValidationError(AinalynError):
    """Validation error"""
    pass


# Infrastructure-layer exception
class ProviderError(AinalynError):
    """Provider call error"""

    def __init__(
        self,
        message: str,
        code: str | None = None,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message, code)
        self.status_code = status_code
        self.response_body = response_body
```

### 6.2 Error Translation

```python
async def call_api(request: Request) -> Response:
    try:
        response = await self._http_client.post(url, json=data)
        response.raise_for_status()
        return Response(**response.json())
    except httpx.HTTPStatusError as e:
        # Translate into SDK exception
        raise ProviderError(
            message=f"API call failed: {e.response.status_code}",
            code="PROVIDER_HTTP_ERROR",
            status_code=e.response.status_code,
            response_body=e.response.text,
        ) from e
    except httpx.RequestError as e:
        raise ProviderError(
            message=f"Network error: {str(e)}",
            code="PROVIDER_NETWORK_ERROR",
        ) from e
```

---

## 7. Documentation Conventions

### 7.1 Docstring Format (Google Style)

```python
async def send_message(
    self,
    message: str,
    session_id: str | None = None,
    stream: bool = False,
) -> ChatResponse:
    """
    Send a chat message.

    Args:
        message: The content of the message to send.
        session_id: Session ID; if None, a new session is created.
        stream: Whether to use streaming mode.

    Returns:
        ChatResponse containing the AI reply and usage information.

    Raises:
        ValidationError: If the message content is invalid.
        ProviderError: If the API call fails.

    Example:
        >>> response = await client.chat.send_message("Hello")
        >>> print(response.content)
        "Hello! How can I help you?"
    """
```

### 7.2 Class Docstring

```python
class ChatClient:
    """
    Chat service client.

    Provides multi-provider chat capabilities with support for
    streaming and non-streaming modes.

    Attributes:
        default_provider: Name of the default provider.
        session_storage: Session storage implementation.

    Example:
        >>> client = ChatClient(api_key="your-key")
        >>> response = await client.send_message("Hello")
    """
```

---

## 8. Test Code Conventions

### 8.1 Test Naming

```python
# Test file
test_chat_client.py

# Test class
class TestChatClient:
    """Unit tests for ChatClient"""

# Test methods
async def test_send_message_returns_response(self):
    """send_message should return a valid ChatResponse"""

async def test_send_message_with_invalid_input_raises_validation_error(self):
    """send_message should raise ValidationError on invalid input"""
```

### 8.2 Test Structure (Arrange-Act-Assert)

```python
async def test_send_message_stores_in_session(self):
    # Arrange
    storage = InMemoryStorage()
    client = ChatClient(storage=storage)
    message = "Hello"

    # Act
    response = await client.send_message(message)

    # Assert
    session = await storage.get_session(response.session_id)
    assert len(session.messages) == 2  # user + assistant
    assert session.messages[0].content == message
```

### 8.3 Using Mocks

```python
from unittest.mock import AsyncMock, MagicMock

async def test_provider_called_with_correct_params(self):
    # Arrange
    mock_provider = AsyncMock(spec=ProviderPort)
    mock_provider.send_request.return_value = ProviderResponse(
        content="Hello!",
        usage=Usage(input_tokens=5, output_tokens=2),
    )
    client = ChatClient(provider=mock_provider)

    # Act
    await client.send_message("Hi")

    # Assert
    mock_provider.send_request.assert_called_once()
    call_args = mock_provider.send_request.call_args
    assert call_args[0][0].content == "Hi"
```

---

## 9. Prohibited Items List

### 9.1 Strictly Prohibited

* ❌ Importing external packages in the Domain layer
* ❌ Using `print()` for logging (use `logging` or the event system)
* ❌ Hard-coding sensitive information (API keys, passwords)
* ❌ Using `*` imports
* ❌ Omitting type annotations
* ❌ Using `Any` unless absolutely necessary
* ❌ Synchronous I/O operations
* ❌ Global mutable state

### 9.2 Should Be Avoided but Has Exceptions

* ⚠️ Returning `dict` directly (prefer dataclasses)
* ⚠️ More than 3 levels of nested conditionals
* ⚠️ Single functions longer than 50 lines
* ⚠️ Single files longer than 500 lines

---

## 10. Code Review Checklist

Before submitting a PR, verify:

* [ ] All linters pass (`ruff`, `mypy`)
* [ ] Code is formatted by `black`
* [ ] All public methods have complete docstrings
* [ ] All new code has corresponding tests
* [ ] Type annotations are complete
* [ ] No TODO/FIXME (or corresponding issues have been created)
* [ ] Layered dependency rules are followed
* [ ] Error handling is appropriate
* [ ] Resources are properly released

---

*Last Updated: 2024-12*
