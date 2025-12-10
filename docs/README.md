# Ainalyn SDK Development Documents

> This directory contains all the technical documents required for internal SDK development.

## Document Index

| Document                                                               | Description                               | Target Audience         |
| ---------------------------------------------------------------------- | ----------------------------------------- | ----------------------- |
| [ARCHITECTURE_FOR_DEVS.md](./ARCHITECTURE_FOR_DEVS.md)                 | Project architecture and layered design   | All developers          |
| [API_SURFACE_AND_EXTENSIBILITY.md](./API_SURFACE_AND_EXTENSIBILITY.md) | Public API and extension points           | All developers          |
| [INTERNAL_CODING_GUIDE.md](./INTERNAL_CODING_GUIDE.md)                 | Coding conventions and standards          | All developers          |
| [ERROR_AND_LOGGING_MODEL.md](./ERROR_AND_LOGGING_MODEL.md)             | Error handling and logging design         | All developers          |
| [TESTING_STRATEGY.md](./TESTING_STRATEGY.md)                           | Testing strategy and guidelines           | All developers          |
| [RUST_INTEGRATION_GUIDE.md](./RUST_INTEGRATION_GUIDE.md)               | Rust module integration guide             | Rust-related developers |
| [CONTRIBUTING_INTERNAL.md](./CONTRIBUTING_INTERNAL.md)                 | Internal contribution guide and workflows | All developers          |
| [COMMIT_CONVENTIONS.md](./COMMIT_CONVENTIONS.md)                       | **Commit conventions and best practices** | All developers          |
| [API_CATALOG.md](./API_CATALOG.md)                                     | Catalog of supported API services         | All developers          |

## Getting Started

### New Developers

1. Read [ARCHITECTURE_FOR_DEVS.md](./ARCHITECTURE_FOR_DEVS.md) to understand the project architecture
2. Read [INTERNAL_CODING_GUIDE.md](./INTERNAL_CODING_GUIDE.md) to understand the coding conventions
3. Read [CONTRIBUTING_INTERNAL.md](./CONTRIBUTING_INTERNAL.md) to understand the development workflow
4. **Read [COMMIT_CONVENTIONS.md](./COMMIT_CONVENTIONS.md) to understand commit conventions** (required for open-source projects)
5. Refer to [API_CATALOG.md](./API_CATALOG.md) to understand the supported API services

### Developing New Features

1. Determine which layer the feature belongs to (see [ARCHITECTURE_FOR_DEVS.md](./ARCHITECTURE_FOR_DEVS.md))
2. Follow the conventions in [INTERNAL_CODING_GUIDE.md](./INTERNAL_CODING_GUIDE.md)
3. Write tests (see [TESTING_STRATEGY.md](./TESTING_STRATEGY.md))
4. Handle errors (see [ERROR_AND_LOGGING_MODEL.md](./ERROR_AND_LOGGING_MODEL.md))

### Extending the SDK

* Understand extension points: [API_SURFACE_AND_EXTENSIBILITY.md](./API_SURFACE_AND_EXTENSIBILITY.md)
* Provider extensions, Storage extensions, Middleware extensions

### Rust Module Development

* Read [RUST_INTEGRATION_GUIDE.md](./RUST_INTEGRATION_GUIDE.md)

## Related Resources

* **API Contracts**: `contracts/openapi/` directory
* **Source Code**: `src/` directory
* **Tests**: `tests/` directory
* **Examples**: `examples/` directory

---

*Last updated: 2024-12*
