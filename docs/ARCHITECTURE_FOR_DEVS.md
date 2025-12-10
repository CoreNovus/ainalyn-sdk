# Ainalyn SDK Developer Architecture Guide

> This document is for internal SDK developers. It explains the project structure, layered design, and development scenario guidelines.

## 1. System Overview

### 1.1 Primary Use Case: Desktop Application Integration

The Ainalyn SDK is designed to serve as a **bridge layer** between a packaged desktop application (Electron .exe) and user-defined customizations. This architecture enables:

- **Desktop Frontend (.exe)**: A black-box UI that users cannot modify directly
- **SDK Server**: A local HTTP/WebSocket server that the frontend communicates with
- **User Extensions**: Custom prompts, models, middleware, and providers that users can develop

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Electron Desktop App (.exe)                       │
│                         (Black-box Frontend)                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTP/WebSocket (localhost:port)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Ainalyn SDK Server                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  REST API    │  │  WebSocket   │  │  SSE Events  │               │
│  │  (Request/   │  │  (Streaming/ │  │  (Push       │               │
│  │   Response)  │  │   Bidirect.) │  │   Events)    │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         └─────────────────┼─────────────────┘                        │
│                           ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Application Layer                          │   │
│  │         ChatClient / TranslationClient / ...                  │   │
│  └──────────────────────────────┬───────────────────────────────┘   │
│                                 │                                    │
│  ┌──────────────────────────────┴───────────────────────────────┐   │
│  │                  User Extension Points                        │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────┐ │   │
│  │  │PromptMgr  │ │ ModelMgr  │ │Middleware │ │CustomProvider │ │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │ User-developed Python modules
                                 │
┌─────────────────────────────────────────────────────────────────────┐
│                      User Extension Modules                          │
│                                                                      │
│   my_extension/                                                      │
│   ├── prompts.py          # Custom system prompts                    │
│   ├── models.py           # Model configuration & selection logic    │
│   ├── middleware.py       # Pre/post-processing logic                │
│   └── providers.py        # Custom AI providers (optional)           │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Design Goals

1. **Separation of Concerns**: Frontend UI is decoupled from backend AI logic
2. **User Extensibility**: Users can customize prompts, models, and processing without modifying the SDK
3. **Local-First**: SDK Server runs locally, ensuring data privacy and low latency
4. **Protocol Agnostic**: Support REST, WebSocket, and SSE for different use cases

## 2. Project Directory Structure

```
ainalyn_sdk/
├── contracts/                    # API contract definitions
│   └── openapi/                  # OpenAPI spec files
│       ├── chat-api.yaml
│       ├── translation-api.yaml
│       └── ...
│
├── src/                          # Source code
│   ├── domain/                   # Domain Layer - Core domain
│   │   ├── models/               # Pure data structures (Message, Request, Response...)
│   │   ├── ports/                # Abstract interfaces (ProviderPort, StoragePort...)
│   │   └── errors/               # Domain-layer error definitions
│   │
│   ├── application/              # Application Layer - Application flows
│   │   ├── clients/              # Core client implementations (orchestrators for each API)
│   │   ├── middleware/           # Middleware definitions and wiring
│   │   ├── usecases/             # Specific use-case flows
│   │   ├── prompt_manager.py     # Prompt management and templating
│   │   └── model_manager.py      # Model configuration and selection
│   │
│   ├── infrastructure/           # Infrastructure Layer - Technical implementations
│   │   ├── providers/            # Provider implementations (HTTP, gRPC...)
│   │   ├── storage/              # Storage implementations (Memory, SQLite...)
│   │   ├── events/               # EventPublisher implementations
│   │   ├── middleware/           # Technical middleware (retry, logging...)
│   │   └── rust/                 # Rust module bindings
│   │
│   ├── server/                   # Server Layer - Local HTTP/WebSocket server
│   │   ├── app.py                # FastAPI/Starlette application
│   │   ├── routes/               # API route handlers
│   │   │   ├── chat.py
│   │   │   ├── translation.py
│   │   │   └── ...
│   │   ├── websocket/            # WebSocket handlers
│   │   │   └── streaming.py
│   │   ├── middleware/           # Server middleware (CORS, auth, logging)
│   │   └── config.py             # Server configuration
│   │
│   └── interface/                # Interface Layer - Public API
│       ├── __init__.py           # Public API entry
│       ├── types.py              # Public type exports
│       └── facades/              # Facade classes for simplified usage
│
├── tests/                        # Tests
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── server/                   # Server integration tests
│   └── fixtures/                 # Test data
│
├── docs/                         # Developer documentation
│   ├── ARCHITECTURE_FOR_DEVS.md  # This document
│   ├── API_SURFACE_AND_EXTENSIBILITY.md
│   ├── INTEGRATION_GUIDE.md      # Desktop app integration guide
│   └── ...
│
├── examples/                     # Example code
│   ├── basic/                    # Basic usage examples
│   └── integration/              # Desktop integration examples
│       ├── basic_server/         # Minimal server startup
│       ├── custom_prompts/       # Custom prompt examples
│       └── custom_provider/      # Custom provider examples
│
└── rust/                         # Rust native modules
    └── src/
```

## 3. Five-Layer Architecture

### 3.1 Dependency Direction Rules

```
┌─────────────────────────────────────────────────────────┐
│                     Server Layer                        │
│      (HTTP/WebSocket server, route handlers, CORS)      │
├─────────────────────────────────────────────────────────┤
│                    Interface Layer                      │
│             (Public exposure and composition)           │
├─────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                    │
│    (Technical implementations: HTTP, DB, Rust binding)  │
├─────────────────────────────────────────────────────────┤
│                   Application Layer                     │
│    (Flow orchestration, middleware, prompt/model mgmt)  │
├─────────────────────────────────────────────────────────┤
│                     Domain Layer                        │
│         (Core models and abstract Port interfaces)      │
└─────────────────────────────────────────────────────────┘

Dependency direction: can only depend "inward" (downwards)
- Domain does not depend on any other layer
- Application only depends on Domain
- Infrastructure may depend on Domain and Application interfaces
- Interface may depend on all layers, but only for composition and export
- Server depends on Interface layer, exposes HTTP/WebSocket endpoints
```

### 3.2 Domain Layer

**Purpose**: Define core concepts and abstract capabilities.

**What should go here:**

* Pure data structures (no framework dependencies)

  * `Message` - conversation message
  * `Request` / `Response` - request/response for each API
  * `Usage` - usage information
  * `Session` - session information
  * `PromptTemplate` - prompt template definition
  * `ModelConfig` - model configuration
* Abstract Port interfaces

  * `ProviderPort` - LLM / AI service provider
  * `StoragePort` - data storage
  * `EventPublisherPort` - event publishing
  * `PromptManagerPort` - prompt management
  * `ModelManagerPort` - model management
* Domain error definitions

**Prohibited:**

* ❌ Importing HTTP clients, ORMs, SQL
* ❌ Any Rust binding related code
* ❌ Any logging framework names
* ❌ Flow control logic

### 3.3 Application Layer

**Purpose**: Orchestrate flows and compose Ports to implement features.

**What should go here:**

* Core client classes (orchestrators for each feature)

  * `ChatClient` - chat service
  * `TranslationClient` - translation service
  * `ImageAnalysisClient` - image analysis service
  * ... other API-specific clients
* Middleware definitions and chain management
* Use-case flows
* **Prompt management** (`PromptManager`)
  * Load and manage system prompts
  * Template variable substitution
  * Feature-specific prompt configuration
* **Model management** (`ModelManager`)
  * Model selection strategies
  * Model parameter configuration
  * Provider routing

**Prohibited:**

* ❌ Direct DB access (no SQL or DB drivers)
* ❌ Direct HTTP requests
* ❌ Direct Rust binding calls
* ❌ Concrete provider class names

### 3.4 Infrastructure Layer

**Purpose**: Implement Port interfaces and handle technical details.

**What should go here:**

* Provider implementations

  * `HttpProvider` - HTTP-based API calls
  * `GrpcProvider` - gRPC-based API calls
  * User-defined custom providers
* Storage implementations

  * `InMemoryStorage` - in-memory storage
  * `SQLiteStorage` - SQLite storage
* EventPublisher implementations
* Rust module wrappers
* Technical middleware

**Prohibited:**

* ❌ Business flow decisions
* ❌ Defining abstract interfaces (this belongs in Domain)
* ❌ Direct public exposure

### 3.5 Interface Layer

**Purpose**: Consolidate and expose public APIs, providing a friendly entry point.

**What should go here:**

* Public type exports
* Main entry classes (such as `AinalynClient`)
* Factory functions with default configurations
* Facades for simplified usage

**Prohibited:**

* ❌ Implementing flows
* ❌ Business logic
* Only exposure and composition should live here

### 3.6 Server Layer (NEW)

**Purpose**: Expose SDK functionality via HTTP/WebSocket for desktop application integration.

**What should go here:**

* FastAPI/Starlette application setup
* REST API route handlers
  * Map HTTP endpoints to SDK client methods
  * Request validation and response formatting
* WebSocket handlers
  * Streaming responses (chat, translation)
  * Real-time progress updates
* SSE (Server-Sent Events) endpoints
  * Push notifications for long-running tasks
* Server middleware
  * CORS configuration (for Electron frontend)
  * Authentication (API key, token)
  * Request logging and metrics
* Configuration management
  * Server port, host, SSL
  * Extension loading paths

**Prohibited:**

* ❌ Business logic (delegate to Application layer)
* ❌ Direct provider calls (use Interface/Application layer)
* ❌ Data model definitions (use Domain layer)

## 4. Development Scenario Guidelines

### Scenario A: Adding a New AI Service

Example: Adding support for a new "Text to Speech" API.

1. **Domain Layer**

   * Add `text_to_speech.py` under `domain/models/`
   * Define data structures such as `TextToSpeechRequest`, `TextToSpeechResponse`
   * If a new Port is required, define it in `domain/ports/`

2. **Application Layer**

   * Add `text_to_speech_client.py` under `application/clients/`
   * Implement the flow orchestration logic

3. **Infrastructure Layer**

   * Implement the corresponding HTTP provider in `infrastructure/providers/`

4. **Interface Layer**

   * Export the new class in `interface/__init__.py`

5. **Server Layer**

   * Add route handler in `server/routes/text_to_speech.py`
   * Register routes in `server/app.py`
   * Add WebSocket handler if streaming is supported

### Scenario B: Adding an HTTP Provider

1. Add an implementation under `infrastructure/providers/`
2. Implement the `ProviderPort` interface
3. Handle HTTP communication details (error translation, retries, etc.)

### Scenario C: Adding Middleware

1. **Business-focused middleware** → place in `application/middleware/`
2. **Technical middleware** (e.g., retry) → place in `infrastructure/middleware/`
3. **Server middleware** (e.g., CORS, auth) → place in `server/middleware/`

### Scenario D: Modifying Domain Models

⚠️ **Note**: Changes in Domain affect the entire project.

1. First evaluate the impact scope
2. Update data structures in `domain/models/`
3. Update all dependent Application and Infrastructure code
4. Update corresponding tests

### Scenario E: Adding a Storage Implementation

1. Add the implementation under `infrastructure/storage/`
2. Implement all methods in the `StoragePort` interface
3. Write corresponding integration tests

### Scenario F: Adding Server Endpoints (NEW)

Example: Adding a new REST endpoint for the desktop frontend.

1. **Create route handler** in `server/routes/`

   ```python
   # server/routes/my_feature.py
   from fastapi import APIRouter
   from ainalyn import AinalynClient

   router = APIRouter(prefix="/api/v1/my-feature")

   @router.post("/action")
   async def perform_action(request: ActionRequest):
       client = get_client()
       result = await client.my_feature.action(request.data)
       return {"success": True, "data": result}
   ```

2. **Register in app.py**

   ```python
   from .routes import my_feature
   app.include_router(my_feature.router)
   ```

3. **Add WebSocket handler** (if streaming required)

   ```python
   # server/websocket/my_feature.py
   @router.websocket("/ws/my-feature")
   async def my_feature_stream(websocket: WebSocket):
       await websocket.accept()
       async for chunk in client.my_feature.stream():
           await websocket.send_json(chunk)
   ```

### Scenario G: User Extension Development (NEW)

This scenario describes how **users** (not SDK developers) create extensions.

1. **Custom Prompts**

   ```python
   # my_extension/prompts.py
   from ainalyn.ports import PromptManagerPort

   class MyPromptManager(PromptManagerPort):
       def get_system_prompt(self, feature: str, context: dict) -> str:
           if feature == "chat":
               return f"You are a helpful assistant for {context.get('company', 'users')}."
           return ""
   ```

2. **Custom Model Selection**

   ```python
   # my_extension/models.py
   from ainalyn.ports import ModelManagerPort

   class MyModelManager(ModelManagerPort):
       def select_model(self, feature: str, context: dict) -> str:
           # Route to different models based on task complexity
           if context.get("complexity") == "high":
               return "gpt-4"
           return "gpt-3.5-turbo"
   ```

3. **Custom Middleware**

   ```python
   # my_extension/middleware.py
   from ainalyn.middleware import Middleware

   class ContentFilterMiddleware(Middleware):
       async def before_request(self, context):
           # Filter sensitive content
           context.request.content = self._filter(context.request.content)
           return context
   ```

4. **Custom Provider** (Advanced)

   ```python
   # my_extension/providers.py
   from ainalyn.ports import ProviderPort

   class OllamaProvider(ProviderPort):
       def __init__(self, base_url: str = "http://localhost:11434"):
           self.base_url = base_url

       async def send_request(self, request, options=None):
           # Call local Ollama API
           ...
   ```

5. **Register Extensions**

   ```python
   # main.py
   from ainalyn import AinalynServer
   from my_extension import MyPromptManager, MyModelManager, ContentFilterMiddleware

   server = AinalynServer(
       prompt_manager=MyPromptManager(),
       model_manager=MyModelManager(),
       middleware=[ContentFilterMiddleware()],
   )
   server.run(port=8080)
   ```

## 5. Supported API Services

The SDK must support the following 16 API services (see `contracts/openapi/` for details):

| Service                  | File                            | Description                      |
| ------------------------ | ------------------------------- | -------------------------------- |
| Chat                     | chat-api.yaml                   | Multi-provider chat service      |
| Translation              | translation-api.yaml            | Multilingual translation service |
| Image Analysis           | image-analysis-api.yaml         | Image analysis and Q&A           |
| Speech to Text           | speech-to-text-api.yaml         | Speech to text                   |
| Speech to Image          | speech-to-image-api.yaml        | Image generation from speech     |
| Sketch to Image          | sketch-to-image-api.yaml        | Image generation from sketches   |
| Sketch to Video          | sketch-to-video-api.yaml        | Video generation from sketches   |
| Video Analysis (YouTube) | video-analysis-youtube-api.yaml | YouTube video analysis           |
| Video Generation         | video-generation-api.yaml       | AI video generation              |
| Text to Music            | text-to-music-api.yaml          | Music generation from text       |
| Image to Music           | image-to-music-api.yaml         | Music generation from images     |
| Travel Planning          | travel-planning-api.yaml        | AI travel planning               |
| Presentation             | presentation-api.yaml           | AI presentation generation       |
| Counseling               | counseling-api.yaml             | AI counseling service            |
| Settings                 | settings-api.yaml               | Settings management              |
| History                  | history-api.yaml                | Unified history records          |

## 6. How to Decide Which Layer Code Belongs To

Use the following checklist:

| Question                                                           | Answer | Layer                                                    |
| ------------------------------------------------------------------ | ------ | -------------------------------------------------------- |
| Are you defining nouns or abstract capabilities?                   | Yes    | Domain                                                   |
| Are you defining a "when X happens, do A→B→C" flow?                | Yes    | Application                                              |
| Do you need to connect to HTTP, DB, file system, Rust binding?     | Yes    | Infrastructure                                           |
| Is the sole purpose to make imports convenient for external users? | Yes    | Interface                                                |
| Are you exposing HTTP/WebSocket endpoints for the desktop app?     | Yes    | Server                                                   |
| Does it involve both business flow and technical details?          | -      | Split it: Flow → Application, Technical → Infrastructure |

## 7. Key Principles

1. **Dependency direction must not be reversed** – inner layers must never depend on outer layers
2. **No business logic in Infrastructure** – keep technical implementations focused
3. **Keep Domain pure** – no framework or technical dependencies
4. **Decouple via Ports** – Application should always see the outside world through Ports
5. **Interface only organizes** – no logic should be written in this layer
6. **Server is a thin adapter** – Server layer only translates HTTP/WebSocket to SDK calls, no business logic
7. **User extensions are first-class** – design all extension points to be easily customizable by end users

---

*Last Updated: 2025-01*
