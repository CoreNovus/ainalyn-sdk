# Ainalyn SDK Documentation

> Developer documentation for extending the Ainalyn desktop application.

## What is Ainalyn SDK?

The Ainalyn SDK enables developers to customize and extend the Ainalyn desktop application. With the SDK, you can:

- **Customize AI Prompts** - Define how the AI responds in each feature
- **Route to Different Models** - Choose which AI model handles each request
- **Add Processing Logic** - Filter, transform, or log requests and responses
- **Connect Custom LLMs** - Use your own AI providers (Ollama, vLLM, etc.)

## Quick Start

### 1. Install

```bash
pip install ainalyn-sdk
```

### 2. Basic Usage

```python
from ainalyn import AinalynServer

# Start the server with default settings
server = AinalynServer()
server.run(port=8080)

# The desktop app will connect to localhost:8080
```

### 3. With Custom Extensions

```python
from ainalyn import AinalynServer
from ainalyn.extensions import PromptProvider, ModelRouter

class MyPrompts(PromptProvider):
    def get_system_prompt(self, feature: str, context: dict | None = None) -> str:
        if feature == "chat":
            return "You are a helpful assistant for Acme Corp."
        return "You are a helpful AI assistant."

server = AinalynServer(prompts=MyPrompts())
server.run(port=8080)
```

## Documentation Index

| Document | Description | Audience |
|----------|-------------|----------|
| [API_SURFACE_AND_EXTENSIBILITY.md](./API_SURFACE_AND_EXTENSIBILITY.md) | Extension API reference | SDK Users |
| [ARCHITECTURE_FOR_DEVS.md](./ARCHITECTURE_FOR_DEVS.md) | Internal architecture | SDK Developers (Internal) |
| [INTERNAL_CODING_GUIDE.md](./INTERNAL_CODING_GUIDE.md) | Coding conventions | SDK Developers (Internal) |
| [ERROR_AND_LOGGING_MODEL.md](./ERROR_AND_LOGGING_MODEL.md) | Error handling reference | All |
| [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) | Testing guidelines | SDK Developers (Internal) |
| [CONTRIBUTING_INTERNAL.md](./CONTRIBUTING_INTERNAL.md) | Contribution workflow | SDK Developers (Internal) |
| [COMMIT_CONVENTIONS.md](./COMMIT_CONVENTIONS.md) | Commit conventions | SDK Developers (Internal) |
| [API_CATALOG.md](./API_CATALOG.md) | Supported AI services | Reference |

## Extension Points Overview

### Prompts (Easy)

Customize system prompts for each feature:

```python
class MyPrompts(PromptProvider):
    def get_system_prompt(self, feature: str, context: dict | None = None) -> str:
        return "Your custom prompt here"
```

### Model Router (Easy)

Control which AI model handles requests:

```python
class MyModelRouter(ModelRouter):
    def select_model(self, feature: str, context: dict | None = None) -> ModelConfig:
        return ModelConfig(provider="openai", model="gpt-4")
```

### Middleware (Medium)

Add pre/post-processing:

```python
class MyMiddleware(Middleware):
    async def before_request(self, context: RequestContext) -> RequestContext:
        # Process before AI request
        return context

    async def after_response(self, context: RequestContext, response: Response) -> Response:
        # Process after AI response
        return response
```

### Custom Provider (Advanced)

Connect your own LLM:

```python
class OllamaProvider(Provider):
    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        # Call your LLM
        ...
```

## Common Use Cases

### 1. Enterprise Deployment

Customize prompts with company guidelines:

```python
class EnterprisePrompts(PromptProvider):
    def __init__(self, guidelines_path: str):
        self.guidelines = open(guidelines_path).read()

    def get_system_prompt(self, feature: str, context: dict | None = None) -> str:
        return f"You are an AI assistant. Follow these guidelines:\n{self.guidelines}"
```

### 2. Cost Optimization

Route simple tasks to cheaper models:

```python
class CostOptimizedRouter(ModelRouter):
    def select_model(self, feature: str, context: dict | None = None) -> ModelConfig:
        complexity = context.get("complexity", "low") if context else "low"

        if complexity == "high":
            return ModelConfig(provider="openai", model="gpt-4")
        return ModelConfig(provider="openai", model="gpt-3.5-turbo")
```

### 3. Local LLM

Run completely offline with Ollama:

```python
server = AinalynServer(
    providers={"ollama": OllamaProvider("http://localhost:11434")},
    model_router=LocalModelRouter(),
)
```

### 4. Content Filtering

Filter sensitive content:

```python
class ContentFilter(Middleware):
    async def after_response(self, context: RequestContext, response: Response) -> Response:
        response.content = self.filter_sensitive(response.content)
        return response
```

## Getting Help

- **API Reference**: See [API_SURFACE_AND_EXTENSIBILITY.md](./API_SURFACE_AND_EXTENSIBILITY.md)
- **Examples**: See `examples/` directory
- **Issues**: Report bugs on GitHub

---

*Last Updated: 2025-01*
