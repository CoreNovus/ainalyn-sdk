# Error Handling and Logging Model

> This document defines the SDK's error classification, handling strategy, and logging design specification.

## 1. Error Classification System

### 1.1 Error Hierarchy Tree

```text
AinalynError (Base Exception)
├── ValidationError           # Validation error
│   ├── InvalidInputError     # Invalid input
│   ├── MissingFieldError     # Missing required field
│   └── TypeMismatchError     # Type mismatch
│
├── ProviderError             # Provider layer error
│   ├── AuthenticationError   # Authentication failed
│   ├── RateLimitError        # Rate limit
│   ├── QuotaExceededError    # Quota exceeded
│   ├── NetworkError          # Network error
│   ├── TimeoutError          # Request timed out
│   └── ServiceUnavailableError # Service unavailable
│
├── StorageError              # Storage layer error
│   ├── ConnectionError       # Connection failed
│   ├── NotFoundError         # Resource not found
│   └── ConflictError         # Resource conflict
│
├── ConfigurationError        # Configuration error
│   ├── MissingConfigError    # Missing configuration
│   └── InvalidConfigError    # Invalid configuration value
│
└── InternalError             # Internal error
    └── UnexpectedError       # Unexpected error
```

### 1.2 Error Code Design

**Format**: `{LAYER}_{CATEGORY}_{SPECIFIC}`

| Layer          | Code Prefix | Description             |
| -------------- | ----------- | ----------------------- |
| Domain         | `DOM_`      | Domain layer error      |
| Application    | `APP_`      | Application layer error |
| Infrastructure | `INF_`      | Infrastructure error    |
| Interface      | `INT_`      | Interface layer error   |

**Complete Error Code List**:

```python
# Validation errors (DOM_VAL_*)
DOM_VAL_INVALID_INPUT = "DOM_VAL_INVALID_INPUT"
DOM_VAL_MISSING_FIELD = "DOM_VAL_MISSING_FIELD"
DOM_VAL_TYPE_MISMATCH = "DOM_VAL_TYPE_MISMATCH"
DOM_VAL_OUT_OF_RANGE = "DOM_VAL_OUT_OF_RANGE"

# Provider errors (INF_PRV_*)
INF_PRV_AUTH_FAILED = "INF_PRV_AUTH_FAILED"
INF_PRV_RATE_LIMITED = "INF_PRV_RATE_LIMITED"
INF_PRV_QUOTA_EXCEEDED = "INF_PRV_QUOTA_EXCEEDED"
INF_PRV_NETWORK_ERROR = "INF_PRV_NETWORK_ERROR"
INF_PRV_TIMEOUT = "INF_PRV_TIMEOUT"
INF_PRV_SERVICE_UNAVAILABLE = "INF_PRV_SERVICE_UNAVAILABLE"
INF_PRV_INVALID_RESPONSE = "INF_PRV_INVALID_RESPONSE"

# Storage errors (INF_STO_*)
INF_STO_CONNECTION_FAILED = "INF_STO_CONNECTION_FAILED"
INF_STO_NOT_FOUND = "INF_STO_NOT_FOUND"
INF_STO_CONFLICT = "INF_STO_CONFLICT"
INF_STO_OPERATION_FAILED = "INF_STO_OPERATION_FAILED"

# Configuration errors (APP_CFG_*)
APP_CFG_MISSING = "APP_CFG_MISSING"
APP_CFG_INVALID = "APP_CFG_INVALID"

# Internal errors (INT_ERR_*)
INT_ERR_UNEXPECTED = "INT_ERR_UNEXPECTED"
```

---

## 2. Exception Class Implementation

### 2.1 Base Exception

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AinalynError(Exception):
    """
    SDK base exception class.

    Attributes:
        message: Error message (developer-facing)
        code: Error code
        details: Additional detailed information
        user_message: User-friendly message (optional)
        recoverable: Whether the error is recoverable
    """

    message: str
    code: str = "INT_ERR_UNEXPECTED"
    details: dict[str, Any] = field(default_factory=dict)
    user_message: str | None = None
    recoverable: bool = False

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict format for API responses"""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details,
            "user_message": self.user_message,
        }
```

### 2.2 Specific Exception Classes

```python
@dataclass
class ValidationError(AinalynError):
    """Validation error"""

    field: str | None = None
    expected: str | None = None
    actual: str | None = None

    def __post_init__(self):
        if self.field:
            self.details["field"] = self.field
        if self.expected:
            self.details["expected"] = self.expected
        if self.actual:
            self.details["actual"] = self.actual


@dataclass
class ProviderError(AinalynError):
    """Provider call error"""

    status_code: int | None = None
    response_body: str | None = None
    retry_after: int | None = None  # seconds

    def __post_init__(self):
        if self.status_code:
            self.details["status_code"] = self.status_code
        if self.retry_after:
            self.details["retry_after"] = self.retry_after


@dataclass
class RateLimitError(ProviderError):
    """Rate limit error"""

    code: str = "INF_PRV_RATE_LIMITED"
    recoverable: bool = True
    user_message: str = "Requests are too frequent, please try again later"


@dataclass
class AuthenticationError(ProviderError):
    """Authentication error"""

    code: str = "INF_PRV_AUTH_FAILED"
    recoverable: bool = False
    user_message: str = "Authentication failed, please check your API key"
```

---

## 3. Error Handling Strategy

### 3.1 Error Handling Responsibility by Layer

| Layer          | Responsibility                                       |
| -------------- | ---------------------------------------------------- |
| Domain         | Define error classes, no error handling              |
| Application    | Flow-level error handling, middleware error chaining |
| Infrastructure | Convert external errors into SDK errors              |
| Interface      | Final error formatting, user feedback                |

### 3.2 Error Conversion Rules

**Infrastructure Layer: External → SDK Errors**

```python
# infrastructure/providers/http_provider.py

async def send_request(self, request: ProviderRequest) -> ProviderResponse:
    try:
        response = await self._client.post(url, json=data, timeout=timeout)
        response.raise_for_status()
        return self._parse_response(response)

    except httpx.HTTPStatusError as e:
        raise self._convert_http_error(e) from e

    except httpx.TimeoutException as e:
        raise TimeoutError(
            message=f"Request timed out after {timeout}s",
            code="INF_PRV_TIMEOUT",
            recoverable=True,
        ) from e

    except httpx.RequestError as e:
        raise NetworkError(
            message=f"Network error: {str(e)}",
            code="INF_PRV_NETWORK_ERROR",
            recoverable=True,
        ) from e


def _convert_http_error(self, error: httpx.HTTPStatusError) -> ProviderError:
    """HTTP error conversion"""
    status = error.response.status_code

    if status == 401:
        return AuthenticationError(
            message="Invalid API key",
            status_code=status,
        )
    elif status == 429:
        retry_after = error.response.headers.get("Retry-After")
        return RateLimitError(
            message="Rate limit exceeded",
            status_code=status,
            retry_after=int(retry_after) if retry_after else None,
        )
    elif status == 402:
        return QuotaExceededError(
            message="API quota exceeded",
            status_code=status,
        )
    elif status >= 500:
        return ServiceUnavailableError(
            message=f"Service error: {status}",
            status_code=status,
            recoverable=True,
        )
    else:
        return ProviderError(
            message=f"HTTP error: {status}",
            code="INF_PRV_HTTP_ERROR",
            status_code=status,
            response_body=error.response.text,
        )
```

### 3.3 Middleware Error Handling

```python
# application/middleware/error_handler.py

class ErrorHandlerMiddleware(Middleware):
    """Unified error handling middleware"""

    async def before_request(self, context: MiddlewareContext) -> MiddlewareContext:
        return context

    async def after_request(
        self,
        context: MiddlewareContext,
        response: ProviderResponse
    ) -> ProviderResponse:
        return response

    async def on_error(
        self,
        context: MiddlewareContext,
        error: Exception
    ) -> None:
        # Log error
        await self._log_error(context, error)

        # Convert non-SDK errors
        if not isinstance(error, AinalynError):
            raise InternalError(
                message=f"Unexpected error: {str(error)}",
                code="INT_ERR_UNEXPECTED",
                details={"original_error": type(error).__name__},
            ) from error

        # Re-raise SDK errors directly
        raise
```

### 3.4 Retry Strategy

```python
# infrastructure/middleware/retry.py

@dataclass
class RetryConfig:
    """Retry configuration"""

    max_attempts: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_errors: tuple[type[AinalynError], ...] = (
        RateLimitError,
        NetworkError,
        TimeoutError,
        ServiceUnavailableError,
    )


class RetryMiddleware(Middleware):
    """Automatic retry middleware"""

    def __init__(self, config: RetryConfig | None = None):
        self.config = config or RetryConfig()

    async def execute(
        self,
        context: MiddlewareContext,
        next_handler: NextHandler,
    ) -> ProviderResponse:
        last_error: AinalynError | None = None

        for attempt in range(self.config.max_attempts):
            try:
                return await next_handler(context)

            except self.config.retryable_errors as e:
                last_error = e

                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt, e)
                    await self._log_retry(context, attempt, delay, e)
                    await asyncio.sleep(delay)

        # All retries failed
        assert last_error is not None
        raise last_error

    def _calculate_delay(self, attempt: int, error: AinalynError) -> float:
        # If retry_after is provided, prefer it
        if isinstance(error, RateLimitError) and error.retry_after:
            return min(error.retry_after, self.config.max_delay)

        # Exponential backoff
        delay = self.config.initial_delay * (
            self.config.exponential_base ** attempt
        )
        delay = min(delay, self.config.max_delay)

        # Add jitter
        if self.config.jitter:
            delay = delay * (0.5 + random.random())

        return delay
```

---

## 4. Logging Model

### 4.1 Log Level Definitions

| Level      | Usage Scenario                                                            |
| ---------- | ------------------------------------------------------------------------- |
| `DEBUG`    | Detailed debugging information (request/response content, internal state) |
| `INFO`     | General operation info (API calls, session creation)                      |
| `WARNING`  | Warnings that do not affect operation (retries, performance warnings)     |
| `ERROR`    | Errors that are recoverable (API failures, validation errors)             |
| `CRITICAL` | Severe errors requiring immediate attention (system failures)             |

### 4.2 Structured Log Format

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class LogEntry:
    """Structured log entry"""

    timestamp: datetime
    level: str  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message: str
    logger_name: str

    # Tracing information
    request_id: str | None = None
    session_id: str | None = None
    user_id: str | None = None

    # Context
    component: str | None = None  # "provider", "storage", "middleware"
    operation: str | None = None  # "send_message", "transcribe"

    # Error information
    error_code: str | None = None
    error_message: str | None = None
    stack_trace: str | None = None

    # Performance metrics
    duration_ms: float | None = None
    tokens_used: int | None = None

    # Extra data
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict format"""
        result = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "logger": self.logger_name,
        }

        # Add non-None fields
        optional_fields = [
            "request_id", "session_id", "user_id",
            "component", "operation",
            "error_code", "error_message", "stack_trace",
            "duration_ms", "tokens_used",
        ]
        for field_name in optional_fields:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value

        if self.extra:
            result["extra"] = self.extra

        return result
```

### 4.3 Logger Implementation

```python
# infrastructure/logging/logger.py

import logging
import json
from typing import Any

class SDKLogger:
    """SDK-specific logger"""

    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        handler: logging.Handler | None = None,
    ):
        self._logger = logging.getLogger(f"ainalyn.{name}")
        self._logger.setLevel(level)

        if handler:
            self._logger.addHandler(handler)
        elif not self._logger.handlers:
            # Default handler
            handler = logging.StreamHandler()
            handler.setFormatter(self._get_default_formatter())
            self._logger.addHandler(handler)

        self._context: dict[str, Any] = {}

    def with_context(self, **kwargs: Any) -> "SDKLogger":
        """Create a logger with context"""
        new_logger = SDKLogger.__new__(SDKLogger)
        new_logger._logger = self._logger
        new_logger._context = {**self._context, **kwargs}
        return new_logger

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, message, **kwargs)

    def error(
        self,
        message: str,
        error: Exception | None = None,
        **kwargs: Any
    ) -> None:
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
            if isinstance(error, AinalynError):
                kwargs["error_code"] = error.code
        self._log(logging.ERROR, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal logging method"""
        combined = {**self._context, **kwargs}
        extra = {"structured_data": combined}
        self._logger.log(level, message, extra=extra)

    @staticmethod
    def _get_default_formatter() -> logging.Formatter:
        """Default formatter"""
        return logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
```

### 4.4 Logging Usage Examples

```python
# Create logger
logger = SDKLogger("chat_client")

# Basic usage
logger.info("Sending message", session_id="sess_123", message_length=100)

# With context
request_logger = logger.with_context(
    request_id="req_abc",
    session_id="sess_123",
)
request_logger.debug("Request started")
request_logger.info("Request completed", duration_ms=150)

# Error logging
try:
    await provider.send_request(request)
except ProviderError as e:
    logger.error("Provider call failed", error=e, provider="openai")
    raise
```

---

## 5. Logging Best Practices

### 5.1 What Should Be Logged

| Scenario             | Level   | Required Information                  |
| -------------------- | ------- | ------------------------------------- |
| API request start    | DEBUG   | request_id, operation, params         |
| API request success  | INFO    | request_id, duration_ms, tokens_used  |
| Retry occurred       | WARNING | request_id, attempt, delay, reason    |
| Recoverable error    | ERROR   | request_id, error_code, error_message |
| Session creation     | INFO    | session_id, user_id                   |
| Configuration change | INFO    | changed_fields                        |

### 5.2 What Should Not Be Logged

* ❌ API keys or other sensitive credentials
* ❌ Full request/response bodies (may contain sensitive data)
* ❌ Users' personal message content
* ❌ Large amounts of repetitive identical messages

### 5.3 Handling Sensitive Data

```python
def sanitize_log_data(data: dict[str, Any]) -> dict[str, Any]:
    """Sanitize sensitive data"""
    sensitive_keys = {"api_key", "password", "token", "secret", "authorization"}
    result = {}

    for key, value in data.items():
        if key.lower() in sensitive_keys:
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = sanitize_log_data(value)
        elif isinstance(value, str) and len(value) > 1000:
            result[key] = f"{value[:100]}...[truncated, length={len(value)}]"
        else:
            result[key] = value

    return result
```

---

## 6. User Error Feedback

### 6.1 Error Response Format

```python
@dataclass
class ErrorResponse:
    """External error response"""

    success: bool = False
    error: str = ""  # Error summary
    code: str = ""   # Error code
    message: str | None = None  # User-friendly message
    details: dict[str, Any] | None = None  # Detailed information


def format_error_response(error: AinalynError) -> ErrorResponse:
    """Convert SDK error into user response"""
    return ErrorResponse(
        success=False,
        error=error.message,
        code=error.code,
        message=error.user_message,
        details=error.details if error.details else None,
    )
```

### 6.2 User-Friendly Message Mapping Table

| Error Code                    | User Message                                                        |
| ----------------------------- | ------------------------------------------------------------------- |
| `INF_PRV_AUTH_FAILED`         | Authentication failed, please check whether your API key is correct |
| `INF_PRV_RATE_LIMITED`        | Requests are too frequent, please try again later                   |
| `INF_PRV_QUOTA_EXCEEDED`      | API quota has been exhausted, please contact the administrator      |
| `INF_PRV_TIMEOUT`             | Request timed out, please try again later                           |
| `INF_PRV_SERVICE_UNAVAILABLE` | Service is temporarily unavailable, please try again later          |
| `DOM_VAL_INVALID_INPUT`       | Invalid input, please verify and try again                          |
| `DOM_VAL_MISSING_FIELD`       | Missing required field(s), please complete all required fields      |

---

*Last updated: 2024-12*
