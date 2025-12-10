# Ainalyn SDK Developer Architecture Guide

> This document is for internal SDK developers. It explains the project structure, layered design, and development scenario guidelines.

## 1. Project Directory Structure

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
│   │   └── usecases/             # Specific use-case flows
│   │
│   ├── infrastructure/           # Infrastructure Layer - Technical implementations
│   │   ├── providers/            # Provider implementations (HTTP, gRPC...)
│   │   ├── storage/              # Storage implementations (Memory, SQLite...)
│   │   ├── events/               # EventPublisher implementations
│   │   ├── middleware/           # Technical middleware (retry, logging...)
│   │   └── rust/                 # Rust module bindings
│   │
│   └── interface/                # Interface Layer - Public API
│       ├── __init__.py           # Public API entry
│       ├── types.py              # Public type exports
│       └── facades/              # Facade classes for simplified usage
│
├── tests/                        # Tests
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
│
├── docs/                         # Developer documentation
│   ├── ARCHITECTURE_FOR_DEVS.md  # This document
│   ├── API_SURFACE_AND_EXTENSIBILITY.md
│   └── ...
│
├── examples/                     # Example code
│
└── rust/                         # Rust native modules
    └── src/
```

## 2. Four-Layer Architecture

### 2.1 Dependency Direction Rules

```
┌─────────────────────────────────────────────────────────┐
│                    Interface Layer                      │
│             (Public exposure and composition)           │
├─────────────────────────────────────────────────────────┤
│                 Infrastructure Layer                    │
│    (Technical implementations: HTTP, DB, Rust binding)  │
├─────────────────────────────────────────────────────────┤
│                   Application Layer                     │
│         (Flow orchestration, middleware chaining)       │
├─────────────────────────────────────────────────────────┤
│                     Domain Layer                        │
│         (Core models and abstract Port interfaces)      │
└─────────────────────────────────────────────────────────┘

Dependency direction: can only depend “inward” (downwards)
- Domain does not depend on any other layer
- Application only depends on Domain
- Infrastructure may depend on Domain and Application interfaces
- Interface may depend on all layers, but only for composition and export
```

### 2.2 Domain Layer

**Purpose**: Define core concepts and abstract capabilities.

**What should go here:**

* Pure data structures (no framework dependencies)

  * `Message` - conversation message
  * `Request` / `Response` - request/response for each API
  * `Usage` - usage information
  * `Session` - session information
* Abstract Port interfaces

  * `ProviderPort` - LLM / AI service provider
  * `StoragePort` - data storage
  * `EventPublisherPort` - event publishing
* Domain error definitions

**Prohibited:**

* ❌ Importing HTTP clients, ORMs, SQL
* ❌ Any Rust binding related code
* ❌ Any logging framework names
* ❌ Flow control logic

### 2.3 Application Layer

**Purpose**: Orchestrate flows and compose Ports to implement features.

**What should go here:**

* Core client classes (orchestrators for each feature)

  * `ChatClient` - chat service
  * `TranslationClient` - translation service
  * `ImageAnalysisClient` - image analysis service
  * ... other API-specific clients
* Middleware definitions and chain management
* Use-case flows

**Prohibited:**

* ❌ Direct DB access (no SQL or DB drivers)
* ❌ Direct HTTP requests
* ❌ Direct Rust binding calls
* ❌ Concrete provider class names

### 2.4 Infrastructure Layer

**Purpose**: Implement Port interfaces and handle technical details.

**What should go here:**

* Provider implementations

  * `HttpProvider` - HTTP-based API calls
  * `GrpcProvider` - gRPC-based API calls
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

### 2.5 Interface Layer

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

## 3. Development Scenario Guidelines

### Scenario A: Adding a New AI Service

Example: Adding support for a new “Text to Speech” API.

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

### Scenario B: Adding an HTTP Provider

1. Add an implementation under `infrastructure/providers/`
2. Implement the `ProviderPort` interface
3. Handle HTTP communication details (error translation, retries, etc.)

### Scenario C: Adding Middleware

1. **Business-focused middleware** → place in `application/middleware/`
2. **Technical middleware** (e.g., retry) → place in `infrastructure/middleware/`

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

## 4. Supported API Services

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

## 5. How to Decide Which Layer Code Belongs To

Use the following checklist:

| Question                                                           | Answer | Layer                                                    |
| ------------------------------------------------------------------ | ------ | -------------------------------------------------------- |
| Are you defining nouns or abstract capabilities?                   | Yes    | Domain                                                   |
| Are you defining a “when X happens, do A→B→C” flow?                | Yes    | Application                                              |
| Do you need to connect to HTTP, DB, file system, Rust binding?     | Yes    | Infrastructure                                           |
| Is the sole purpose to make imports convenient for external users? | Yes    | Interface                                                |
| Does it involve both business flow and technical details?          | -      | Split it: Flow → Application, Technical → Infrastructure |

## 6. Key Principles

1. **Dependency direction must not be reversed** – inner layers must never depend on outer layers
2. **No business logic in Infrastructure** – keep technical implementations focused
3. **Keep Domain pure** – no framework or technical dependencies
4. **Decouple via Ports** – Application should always see the outside world through Ports
5. **Interface only organizes** – no logic should be written in this layer

---

*Last Updated: 2024-12*
