# SDK Extension API Reference

> This document describes the extension points available to users who want to customize the SDK behavior for their desktop application integration.

## 1. Overview

The Ainalyn SDK allows you to customize how the desktop application interacts with AI services. You can extend:

| Extension Point | Purpose | Difficulty |
|-----------------|---------|------------|
| **Prompts** | Customize system prompts for each feature | Easy |
| **Model Router** | Control which AI model is used | Easy |
| **Middleware** | Add pre/post-processing logic | Medium |
| **Custom Provider** | Connect your own LLM (e.g., Ollama, vLLM) | Advanced |

## 2. Getting Started

### 2.1 Basic Server Startup

```python
from ainalyn import AinalynServer

# Start the server with default settings
server = AinalynServer()
server.run(port=8080)
```

### 2.2 Server with Custom Extensions

```python
from ainalyn import AinalynServer
from my_extensions import MyPrompts, MyModelRouter, MyMiddleware

server = AinalynServer(
    prompts=MyPrompts(),
    model_router=MyModelRouter(),
    middleware=[MyMiddleware()],
)
server.run(port=8080)
```

---

## 3. Prompt Customization

Prompts define how the AI behaves. You can customize system prompts for each feature.

### 3.1 PromptProvider Interface

```python
from ainalyn.extensions import PromptProvider
from typing import Protocol

class PromptProvider(Protocol):
    """Interface for custom prompt providers"""

    def get_system_prompt(
        self,
        feature: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Return the system prompt for a given feature.

        Args:
            feature: The feature requesting the prompt.
                     One of: "chat", "translation", "counseling",
                     "image_analysis", "travel_planning", etc.
            context: Optional context with user/session info.

        Returns:
            The system prompt string.
        """
        ...
```

### 3.2 Example: Custom Prompt Provider

```python
from ainalyn.extensions import PromptProvider

class MyPrompts(PromptProvider):
    """Custom prompts for enterprise deployment"""

    def __init__(self, company_name: str = "Acme Corp"):
        self.company_name = company_name

    def get_system_prompt(self, feature: str, context: dict | None = None) -> str:
        base = f"You are an AI assistant for {self.company_name}."

        if feature == "chat":
            return f"""
{base}

Guidelines:
- Be professional and helpful
- Do not discuss competitors
- If unsure, say "I'll need to check on that"
"""

        if feature == "translation":
            return f"{base} Provide accurate, natural translations."

        if feature == "counseling":
            style = context.get("style", "empathetic") if context else "empathetic"
            return f"{base} Respond in a {style} manner."

        return base

# Usage
server = AinalynServer(prompts=MyPrompts("Acme Corp"))
```

### 3.3 Available Features

| Feature | Description | Default Prompt Behavior |
|---------|-------------|------------------------|
| `chat` | General chat | Helpful assistant |
| `translation` | Text translation | Accurate translator |
| `counseling` | Counseling service | Empathetic counselor |
| `image_analysis` | Image Q&A | Visual analyst |
| `travel_planning` | Travel planning | Travel expert |
| `presentation` | Presentation generation | Presentation designer |

---

## 4. Model Router

Control which AI model handles each request.

### 4.1 ModelRouter Interface

```python
from ainalyn.extensions import ModelRouter, ModelConfig
from typing import Protocol

class ModelRouter(Protocol):
    """Interface for custom model routing"""

    def select_model(
        self,
        feature: str,
        context: dict[str, Any] | None = None,
    ) -> ModelConfig:
        """
        Select the model for a request.

        Args:
            feature: The feature making the request.
            context: Request context (may include user_id, complexity, etc.)

        Returns:
            ModelConfig specifying provider, model, and parameters.
        """
        ...

    def get_available_models(self) -> list[ModelInfo]:
        """Return list of available models for UI display."""
        ...


@dataclass
class ModelConfig:
    """Model configuration"""
    provider: str           # "openai", "anthropic", "google", or custom
    model: str              # Model name (e.g., "gpt-4", "claude-3-opus")
    temperature: float = 0.7
    max_tokens: int = 4096
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelInfo:
    """Model information for UI"""
    id: str
    name: str
    provider: str
    description: str = ""
```

### 4.2 Example: Custom Model Router

```python
from ainalyn.extensions import ModelRouter, ModelConfig, ModelInfo

class MyModelRouter(ModelRouter):
    """Route to different models based on task and user"""

    def select_model(self, feature: str, context: dict | None = None) -> ModelConfig:
        context = context or {}

        # High complexity tasks get GPT-4
        if context.get("complexity") == "high":
            return ModelConfig(
                provider="openai",
                model="gpt-4",
                temperature=0.7,
            )

        # Translation uses a specialized model
        if feature == "translation":
            return ModelConfig(
                provider="google",
                model="gemini-pro",
                temperature=0.3,
            )

        # Premium users get Claude
        if context.get("user_tier") == "premium":
            return ModelConfig(
                provider="anthropic",
                model="claude-3-opus",
            )

        # Default: cost-effective model
        return ModelConfig(
            provider="openai",
            model="gpt-3.5-turbo",
        )

    def get_available_models(self) -> list[ModelInfo]:
        return [
            ModelInfo("gpt-4", "GPT-4", "openai", "Most capable"),
            ModelInfo("gpt-3.5-turbo", "GPT-3.5", "openai", "Fast & affordable"),
            ModelInfo("claude-3-opus", "Claude 3 Opus", "anthropic", "Best for analysis"),
        ]

# Usage
server = AinalynServer(model_router=MyModelRouter())
```

---

## 5. Middleware

Add custom processing before and after AI requests.

### 5.1 Middleware Interface

```python
from ainalyn.extensions import Middleware, RequestContext, Response
from typing import Protocol

class Middleware(Protocol):
    """Interface for request/response middleware"""

    async def before_request(
        self,
        context: RequestContext,
    ) -> RequestContext:
        """
        Process before the AI request.

        Use cases:
        - Input validation
        - Content filtering
        - Adding context
        - Logging

        Args:
            context: The request context (mutable)

        Returns:
            Modified context
        """
        return context

    async def after_response(
        self,
        context: RequestContext,
        response: Response,
    ) -> Response:
        """
        Process after the AI response.

        Use cases:
        - Output filtering
        - Response formatting
        - Logging
        - Analytics

        Args:
            context: The original request context
            response: The AI response (mutable)

        Returns:
            Modified response
        """
        return response

    async def on_error(
        self,
        context: RequestContext,
        error: Exception,
    ) -> None:
        """
        Handle errors (for logging/alerting, not recovery).

        Args:
            context: The request context
            error: The exception that occurred
        """
        pass
```

### 5.2 Example: Content Filter Middleware

```python
from ainalyn.extensions import Middleware, RequestContext, Response

class ContentFilterMiddleware(Middleware):
    """Filter sensitive content from inputs and outputs"""

    def __init__(self, blocked_words: list[str]):
        self.blocked_words = [w.lower() for w in blocked_words]

    async def before_request(self, context: RequestContext) -> RequestContext:
        # Filter input
        content = context.request.content.lower()
        for word in self.blocked_words:
            if word in content:
                context.request.content = "[Content filtered]"
                break
        return context

    async def after_response(self, context: RequestContext, response: Response) -> Response:
        # Filter output
        for word in self.blocked_words:
            if word in response.content.lower():
                response.content = response.content.replace(word, "[filtered]")
        return response

# Usage
server = AinalynServer(
    middleware=[ContentFilterMiddleware(["confidential", "secret"])]
)
```

### 5.3 Example: Logging Middleware

```python
import logging
from ainalyn.extensions import Middleware, RequestContext, Response

class LoggingMiddleware(Middleware):
    """Log all requests and responses"""

    def __init__(self):
        self.logger = logging.getLogger("ainalyn.requests")

    async def before_request(self, context: RequestContext) -> RequestContext:
        self.logger.info(f"Request: feature={context.feature}, length={len(context.request.content)}")
        return context

    async def after_response(self, context: RequestContext, response: Response) -> Response:
        self.logger.info(f"Response: tokens={response.usage.total_tokens}")
        return response

    async def on_error(self, context: RequestContext, error: Exception) -> None:
        self.logger.error(f"Error: {error}")
```

### 5.4 Middleware Execution Order

```
Request Flow:
  1. Middleware[0].before_request()
  2. Middleware[1].before_request()
  3. ... (all middleware)
  4. AI Request
  5. Middleware[N].after_response()  (reverse order)
  6. Middleware[N-1].after_response()
  7. ... (all middleware, reversed)
```

---

## 6. Custom Provider (Advanced)

Connect your own LLM backend (e.g., Ollama, vLLM, private deployment).

### 6.1 Provider Interface

```python
from ainalyn.extensions import Provider, ProviderRequest, ProviderResponse
from typing import Protocol, AsyncIterator

class Provider(Protocol):
    """Interface for custom AI providers"""

    async def generate(
        self,
        request: ProviderRequest,
    ) -> ProviderResponse:
        """
        Generate a response (non-streaming).

        Args:
            request: The generation request

        Returns:
            The complete response
        """
        ...

    async def stream(
        self,
        request: ProviderRequest,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response.

        Args:
            request: The generation request

        Yields:
            Response chunks as strings
        """
        ...

    def get_models(self) -> list[str]:
        """Return list of available model names."""
        ...


@dataclass
class ProviderRequest:
    """Request to the provider"""
    messages: list[Message]      # Conversation messages
    model: str                   # Model name
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False


@dataclass
class ProviderResponse:
    """Response from the provider"""
    content: str
    usage: Usage
    model: str
    finish_reason: str = "stop"
```

### 6.2 Example: Ollama Provider

```python
import httpx
from ainalyn.extensions import Provider, ProviderRequest, ProviderResponse
from typing import AsyncIterator

class OllamaProvider(Provider):
    """Provider for local Ollama instance"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        response = await self.client.post(
            "/api/chat",
            json={
                "model": request.model,
                "messages": [
                    {"role": m.role, "content": m.content}
                    for m in request.messages
                ],
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                },
            },
        )
        data = response.json()

        return ProviderResponse(
            content=data["message"]["content"],
            usage=Usage(
                input_tokens=data.get("prompt_eval_count", 0),
                output_tokens=data.get("eval_count", 0),
            ),
            model=request.model,
        )

    async def stream(self, request: ProviderRequest) -> AsyncIterator[str]:
        async with self.client.stream(
            "POST",
            "/api/chat",
            json={
                "model": request.model,
                "messages": [
                    {"role": m.role, "content": m.content}
                    for m in request.messages
                ],
                "stream": True,
            },
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data:
                        yield data["message"].get("content", "")

    def get_models(self) -> list[str]:
        return ["llama2", "mistral", "codellama"]

# Usage
server = AinalynServer(
    providers={"ollama": OllamaProvider()},
    model_router=OllamaModelRouter(),  # Route to "ollama" provider
)
```

### 6.3 Using Custom Provider with Model Router

```python
class OllamaModelRouter(ModelRouter):
    """Route all requests to local Ollama"""

    def select_model(self, feature: str, context: dict | None = None) -> ModelConfig:
        return ModelConfig(
            provider="ollama",  # Use the custom provider
            model="llama2",
            temperature=0.7,
        )
```

---

## 7. Configuration

### 7.1 Server Configuration

```python
from ainalyn import AinalynServer, ServerConfig

config = ServerConfig(
    host="127.0.0.1",       # Localhost only (recommended for security)
    port=8080,               # Port number
    cors_origins=["*"],      # CORS origins (Electron app)
    log_level="INFO",        # Logging level
    api_key=None,            # Optional: require API key for requests
)

server = AinalynServer(config=config)
```

### 7.2 Configuration File (Optional)

```yaml
# config.yaml
server:
  host: "127.0.0.1"
  port: 8080
  log_level: "INFO"

extensions:
  prompts_module: "my_extensions.prompts"
  model_router_module: "my_extensions.models"
  middleware_modules:
    - "my_extensions.logging"
    - "my_extensions.filters"
```

```python
from ainalyn import AinalynServer

server = AinalynServer.from_config("config.yaml")
server.run()
```

---

## 8. Best Practices

### 8.1 Prompt Engineering Tips

1. **Be Specific**: Clear instructions produce better results
2. **Use Context**: Pass user info via `context` parameter
3. **Test Variations**: Try different prompts for each feature
4. **Keep It Focused**: One role per prompt

### 8.2 Model Router Tips

1. **Cost Optimization**: Use cheaper models for simple tasks
2. **Quality Routing**: Route complex tasks to capable models
3. **Fallback Logic**: Have backup models if primary fails

### 8.3 Middleware Tips

1. **Keep It Light**: Don't add heavy processing
2. **Order Matters**: Put logging first, filters last
3. **Don't Modify Original**: Create copies when transforming
4. **Handle Errors**: Always implement `on_error`

### 8.4 Custom Provider Tips

1. **Handle Timeouts**: Set reasonable timeout values
2. **Implement Retry**: Add retry logic for transient failures
3. **Normalize Responses**: Match the expected response format
4. **Test Thoroughly**: Test both streaming and non-streaming

---

## 9. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Server won't start | Port in use | Change port in config |
| CORS errors | Origin not allowed | Add Electron origin to `cors_origins` |
| Model not found | Wrong provider/model | Check `model_router` returns valid config |
| Timeout errors | Slow provider | Increase timeout or use faster model |

### Debug Mode

```python
server = AinalynServer(
    config=ServerConfig(log_level="DEBUG"),
)
```

---

*Last Updated: 2025-01*
