# Public API and Extension Points

> This document defines the Public APIs that the SDK guarantees externally, as well as user-extensible Extension Points.

## 1. Public API Overview

### 1.1 Main Entry Points

The SDK provides two main entry points depending on the use case:

#### For Direct SDK Usage

```python
from ainalyn import AinalynClient

# Create a Client instance
client = AinalynClient(
    api_key="your-api-key",
    base_url="https://api.corenovus.com",  # optional
    storage=None,  # optional, custom Storage
    middleware=None,  # optional, custom Middleware
)
```

#### For Desktop Application Integration (Server Mode)

```python
from ainalyn import AinalynServer

# Create and run a local server for desktop app integration
server = AinalynServer(
    api_key="your-api-key",
    host="127.0.0.1",           # localhost only for security
    port=8080,                   # configurable port
    cors_origins=["app://*"],    # allow Electron app
    prompt_manager=None,         # optional, custom PromptManager
    model_manager=None,          # optional, custom ModelManager
    middleware=None,             # optional, custom Middleware
    providers=None,              # optional, custom Providers
)

# Start the server
server.run()
```

**Responsibilities & Guarantees:**

* `AinalynClient` is the unified entry point for programmatic SDK usage
* `AinalynServer` is the entry point for desktop application integration
* Both manage client instances for all sub-services
* Responsible for configuration propagation and resource management

### 1.2 Service Clients

Each API service has a corresponding client:

| Service          | Client Class            | Main Methods                                                    |
| ---------------- | ----------------------- | --------------------------------------------------------------- |
| Chat             | `ChatClient`            | `send_message()`, `stream_message()`, `create_session()`        |
| Translation      | `TranslationClient`     | `detect_language()`, `translate()`, `upload_document()`         |
| Image Analysis   | `ImageAnalysisClient`   | `analyze()`, `describe()`, `detect_objects()`, `extract_text()` |
| Speech to Text   | `SpeechToTextClient`    | `transcribe()`, `transcribe_async()`, `stream()`                |
| Speech to Image  | `SpeechToImageClient`   | `generate()`, `generate_batch()`                                |
| Sketch to Image  | `SketchToImageClient`   | `generate()`, `get_status()`                                    |
| Sketch to Video  | `SketchToVideoClient`   | `generate_image()`, `image_to_video()`, `get_status()`          |
| Video Analysis   | `VideoAnalysisClient`   | `analyze_youtube()`, `chat()`, `validate_url()`                 |
| Video Generation | `VideoGenerationClient` | `upload_images()`, `create_task()`, `get_status()`              |
| Text to Music    | `TextToMusicClient`     | `generate()`, `get_status()`, `download()`                      |
| Image to Music   | `ImageToMusicClient`    | `generate()`, `get_status()`, `download()`                      |
| Travel Planning  | `TravelPlanningClient`  | `plan()`, `stream_plan()`, `get_templates()`                    |
| Presentation     | `PresentationClient`    | `generate()`, `get_status()`, `export()`                        |
| Counseling       | `CounselingClient`      | `send_message()`, `stream_message()`, `create_session()`        |
| Settings         | `SettingsClient`        | `get_settings()`, `update_settings()`, `reset()`                |
| History          | `HistoryClient`         | `get_history()`, `delete()`, `export()`                         |

### 1.3 Core Data Types

**Public domain types:**

```python
from ainalyn.types import (
    # Common
    Message,
    Session,
    Usage,
    Pagination,

    # Chat
    ChatMessage,
    ChatSession,
    ChatProvider,
    ChatModel,

    # Translation
    TranslationConfig,
    TranslationResult,
    DetectedLanguage,

    # Image
    ImageInfo,
    ImageMetadata,
    DetectedObject,
    BoundingBox,

    # Audio/Speech
    TranscribedWord,
    SpeakerSegment,
    GeneratedMusic,

    # Video
    VideoMetadata,
    VideoResult,
    GenerationStatus,

    # Others...
)
```

### 1.4 API Response Structure

All API responses follow a unified structure:

```python
@dataclass
class ApiResponse[T]:
    success: bool
    data: T | None
    error: str | None
    message: str | None
    code: str | None
    metadata: ResponseMetadata | None

@dataclass
class ResponseMetadata:
    request_id: str
    timestamp: datetime
    processing_time: float  # seconds
```

---

## 2. Extension Points

The SDK is designed to be highly extensible for desktop application integration. Users can customize:

1. **Prompt Management** - Define system prompts and templates
2. **Model Management** - Control model selection and routing
3. **Providers** - Implement custom AI service providers
4. **Storage** - Customize data persistence
5. **Middleware** - Add pre/post-processing logic
6. **Events** - Subscribe to SDK events for UI updates

### 2.1 Prompt Manager Extensions (NEW)

Users can customize system prompts for each feature:

```python
from ainalyn.ports import PromptManagerPort
from typing import Protocol

class PromptManagerPort(Protocol):
    """Interface for custom prompt management"""

    def get_system_prompt(
        self,
        feature: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Get the system prompt for a specific feature.

        Args:
            feature: Feature name (e.g., "chat", "translation", "counseling")
            context: Optional context for dynamic prompt generation

        Returns:
            The system prompt string
        """
        ...

    def get_prompt_template(
        self,
        template_name: str,
    ) -> PromptTemplate | None:
        """
        Get a named prompt template.

        Args:
            template_name: Name of the template

        Returns:
            PromptTemplate or None if not found
        """
        ...

    def render_template(
        self,
        template_name: str,
        variables: dict[str, Any],
    ) -> str:
        """
        Render a template with variables.

        Args:
            template_name: Name of the template
            variables: Variables to substitute

        Returns:
            Rendered prompt string
        """
        ...
```

**Usage:**

```python
from ainalyn.ports import PromptManagerPort

class MyPromptManager(PromptManagerPort):
    """Custom prompt manager for enterprise deployment"""

    def __init__(self, company_name: str, guidelines_path: str):
        self.company_name = company_name
        self.guidelines = self._load_guidelines(guidelines_path)

    def get_system_prompt(self, feature: str, context: dict | None = None) -> str:
        base_prompt = f"You are an AI assistant for {self.company_name}."

        if feature == "chat":
            return f"{base_prompt}\n\nGuidelines:\n{self.guidelines}"
        elif feature == "translation":
            return f"{base_prompt}\nProvide accurate translations."
        elif feature == "counseling":
            style = context.get("style", "professional") if context else "professional"
            return f"{base_prompt}\nRespond in a {style} manner."

        return base_prompt

# Register with server
server = AinalynServer(
    prompt_manager=MyPromptManager("Acme Corp", "guidelines.txt"),
)
```

**Invocation timing:**

* `get_system_prompt()`: Called before each AI request to construct the system message
* `get_prompt_template()`: Called when using named templates
* `render_template()`: Called to substitute variables in templates

### 2.2 Model Manager Extensions (NEW)

Users can control model selection and configuration:

```python
from ainalyn.ports import ModelManagerPort
from typing import Protocol

class ModelManagerPort(Protocol):
    """Interface for custom model management"""

    def select_model(
        self,
        feature: str,
        context: dict[str, Any] | None = None,
    ) -> ModelConfig:
        """
        Select the appropriate model for a request.

        Args:
            feature: Feature name (e.g., "chat", "translation")
            context: Request context (user info, task complexity, etc.)

        Returns:
            ModelConfig with provider, model name, and parameters
        """
        ...

    def get_available_models(
        self,
        feature: str | None = None,
    ) -> list[ModelInfo]:
        """
        Get list of available models.

        Args:
            feature: Optional feature filter

        Returns:
            List of available ModelInfo
        """
        ...

    def get_model_config(
        self,
        model_id: str,
    ) -> ModelConfig | None:
        """
        Get configuration for a specific model.

        Args:
            model_id: Model identifier

        Returns:
            ModelConfig or None if not found
        """
        ...
```

**Usage:**

```python
from ainalyn.ports import ModelManagerPort
from ainalyn.types import ModelConfig

class MyModelManager(ModelManagerPort):
    """Custom model manager with intelligent routing"""

    def select_model(self, feature: str, context: dict | None = None) -> ModelConfig:
        context = context or {}

        # Route based on task complexity
        complexity = context.get("complexity", "normal")
        if complexity == "high":
            return ModelConfig(
                provider="openai",
                model="gpt-4",
                temperature=0.7,
                max_tokens=4096,
            )

        # Route based on feature
        if feature == "translation":
            return ModelConfig(
                provider="google",
                model="gemini-pro",
                temperature=0.3,
            )

        # Route based on user tier
        user_tier = context.get("user_tier", "free")
        if user_tier == "premium":
            return ModelConfig(provider="anthropic", model="claude-3-opus")

        # Default model
        return ModelConfig(provider="openai", model="gpt-3.5-turbo")

    def get_available_models(self, feature: str | None = None) -> list[ModelInfo]:
        return [
            ModelInfo(id="gpt-4", provider="openai", name="GPT-4"),
            ModelInfo(id="gpt-3.5-turbo", provider="openai", name="GPT-3.5 Turbo"),
            ModelInfo(id="claude-3-opus", provider="anthropic", name="Claude 3 Opus"),
        ]

# Register with server
server = AinalynServer(
    model_manager=MyModelManager(),
)
```

**Invocation timing:**

* `select_model()`: Called before each AI request to determine which model to use
* `get_available_models()`: Called by frontend to populate model selection dropdowns
* `get_model_config()`: Called when user explicitly selects a model

### 2.3 Provider Extensions

Users can implement custom AI service providers:

```python
from ainalyn.ports import ProviderPort

class CustomProvider(ProviderPort):
    """Interface that a custom Provider must implement"""

    async def send_request(
        self,
        request: ProviderRequest,
        options: ProviderOptions | None = None
    ) -> ProviderResponse:
        """
        Send a request to the AI service

        Args:
            request: Normalized request object
            options: Extra options (timeout, retry, etc.)

        Returns:
            Normalized response object

        Raises:
            ProviderError: When the service call fails
        """
        ...

    async def stream_request(
        self,
        request: ProviderRequest,
        options: ProviderOptions | None = None
    ) -> AsyncIterator[ProviderChunk]:
        """
        Streaming request (if applicable)
        """
        ...

    def validate_config(self) -> ValidationResult:
        """
        Validate provider configuration
        """
        ...
```

**Usage:**

```python
# Use custom Provider
client = AinalynClient(
    api_key="key",
    providers={
        "chat": MyCustomChatProvider(config),
    }
)
```

**Invocation timing:**

* `send_request()`: On every non-streaming API call
* `stream_request()`: On every streaming API call
* `validate_config()`: On initialization and config updates

### 2.4 Storage Extensions

Users can customize data storage:

```python
from ainalyn.ports import StoragePort

class CustomStorage(StoragePort):
    """Interface that a custom Storage must implement"""

    # Session operations
    async def save_session(self, session: Session) -> str:
        """Save a Session and return session_id"""
        ...

    async def get_session(self, session_id: str) -> Session | None:
        """Get a Session"""
        ...

    async def update_session(self, session: Session) -> None:
        """Update a Session"""
        ...

    async def delete_session(self, session_id: str) -> None:
        """Delete a Session"""
        ...

    # Message operations
    async def save_message(self, session_id: str, message: Message) -> str:
        """Save a message and return message_id"""
        ...

    async def get_messages(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[Message]:
        """Get message list"""
        ...

    # Invocation operations
    async def save_invocation(self, invocation: Invocation) -> str:
        """Save API invocation record"""
        ...

    async def get_invocations(
        self,
        session_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100
    ) -> list[Invocation]:
        """Query invocation records"""
        ...

    # Cache operations (optional)
    async def get_cache(self, key: str) -> CacheEntry | None:
        """Get cache entry"""
        ...

    async def set_cache(
        self,
        key: str,
        value: CacheEntry,
        ttl: int | None = None
    ) -> None:
        """Set cache entry"""
        ...
```

**Usage:**

```python
# Use custom Storage
client = AinalynClient(
    api_key="key",
    storage=MyPostgresStorage(connection_string)
)
```

**Invocation timing:**

* Session-related: when creating/retrieving/updating sessions
* Message-related: automatically called after sending messages
* Invocation-related: automatically recorded after each API call

### 2.5 Middleware Extensions

Users can insert custom pre/post request processing:

```python
from ainalyn.middleware import Middleware, MiddlewareContext

class CustomMiddleware(Middleware):
    """Interface that a custom Middleware must implement"""

    async def before_request(
        self,
        context: MiddlewareContext
    ) -> MiddlewareContext:
        """
        Pre-request processing

        Can be used for:
        - Modifying request content
        - Adding tracing IDs
        - Validation/review
        - Logging
        """
        # Modify context.request
        return context

    async def after_request(
        self,
        context: MiddlewareContext,
        response: ProviderResponse
    ) -> ProviderResponse:
        """
        Post-request processing

        Can be used for:
        - Modifying response content
        - Logging
        - Updating statistics
        """
        return response

    async def on_error(
        self,
        context: MiddlewareContext,
        error: Exception
    ) -> None:
        """
        Error handling

        Can be used for:
        - Error logging
        - Alerts/notifications
        """
        ...
```

**Usage:**

```python
# Use custom Middleware
client = AinalynClient(
    api_key="key",
    middleware=[
        LoggingMiddleware(),
        AuditMiddleware(),
        MyCustomMiddleware(),
    ]
)
```

**Execution order:**

1. `before_request`: executed in list order
2. Actual API call
3. `after_request`: executed in **reverse** list order
4. `on_error`: executed in reverse order when an error occurs

### 2.6 Event Extensions

Users can subscribe to SDK events:

```python
from ainalyn.events import EventPublisherPort, Event

class CustomEventHandler(EventPublisherPort):
    """Custom event handler"""

    async def on_token(self, event: TokenEvent) -> None:
        """
        Triggered when each token is received during streaming responses

        Can be used for:
        - Real-time UI updates
        - Progress tracking
        """
        ...

    async def on_complete(self, event: CompleteEvent) -> None:
        """
        Triggered when a request is completed

        Can be used for:
        - Completion notifications
        - Statistics logging
        """
        ...

    async def on_error(self, event: ErrorEvent) -> None:
        """
        Triggered when an error occurs
        """
        ...

    async def on_progress(self, event: ProgressEvent) -> None:
        """
        Progress updates for long-running tasks

        Applicable to:
        - Video generation
        - Music generation
        - Document translation
        """
        ...
```

**Usage:**

```python
# Use custom event handlers
client = AinalynClient(
    api_key="key",
    event_handlers=[
        MyUIEventHandler(),
        MyLoggingEventHandler(),
    ]
)
```

---

## 3. Built-in Implementations

The SDK provides the following built-in implementations:

### 3.1 Built-in Provider

| Provider       | Description                       |
| -------------- | --------------------------------- |
| `HttpProvider` | Standard HTTP API calls (default) |

### 3.2 Built-in Storage

| Storage           | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| `InMemoryStorage` | In-memory storage (default, suitable for development/testing) |
| `SQLiteStorage`   | SQLite file storage (suitable for single-node apps)           |

### 3.3 Built-in Middleware

| Middleware             | Description                                 |
| ---------------------- | ------------------------------------------- |
| `RetryMiddleware`      | Automatic retries for failed requests       |
| `RateLimitMiddleware`  | Request rate limiting                       |
| `LoggingMiddleware`    | Request logging                             |
| `TokenLimitMiddleware` | Token usage limiting (requires Rust module) |
| `CacheMiddleware`      | Response caching                            |

---

## 4. Version Compatibility Guarantees

### 4.1 Public API Stability

* **Stable**: Main entry point (`AinalynClient`) and public methods of service clients
* **Stable**: Data types exported from the `types` module
* **Stable**: Port interfaces (`ProviderPort`, `StoragePort`, etc.)

### 4.2 Possible Changes

* **Subject to change**: Internal implementation details of built-in middleware
* **Subject to change**: Error message text
* **Subject to change**: Non-essential fields in `ResponseMetadata`

### 4.3 Deprecation Policy

* Deprecated items are marked with a `@deprecated` warning before removal
* A transition period of at least 2 minor versions is provided
* Removal only occurs in major version upgrades

---

## 5. Extension Development Checklist

When developing custom extensions, please verify:

**Provider:**

* [ ] All required methods are implemented
* [ ] Errors are handled correctly and converted to `ProviderError`
* [ ] Cancellation is supported (if applicable)
* [ ] Corresponding tests are written

**Storage:**

* [ ] All Session/Message/Invocation methods are implemented
* [ ] Thread safety is ensured (if needed)
* [ ] Connection failures are handled
* [ ] Integration tests are written

**Middleware:**

* [ ] Do not raise directly inside middleware (use `context.abort()`)
* [ ] Context is passed correctly
* [ ] Execution order side effects are considered
* [ ] Unit tests are written

**Event Handler:**

* [ ] Handler methods are non-blocking
* [ ] Internal errors do not affect the main flow
* [ ] Performance impact under high-frequency calls is considered

---

*Last Updated: 2024-12*
