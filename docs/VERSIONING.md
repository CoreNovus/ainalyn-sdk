# Documentation Versioning Strategy

This document describes how we manage documentation versions for the Ainalyn SDK.

## Why Version Documentation?

Users need documentation that matches the SDK version they're using. Without versioned docs, users may follow instructions that don't work with their installed version.

**Key principle**: Documentation should always match the release version to prevent confusion and errors.

## Versioning Strategy

### Current State (v0.1.0)

- **Single version**: Documentation is for the latest release (0.1.0)
- **Deployment**: GitHub Pages with automatic deployment on main branch
- **No multi-version support yet**: Will be added when we reach v0.2.0

### Future State (v0.2.0+)

We will use **[mike](https://github.com/jimporter/mike)** to manage multiple documentation versions:

```bash
# Deploy docs for version 1.0
mike deploy 1.0 latest --update-aliases

# Deploy docs for version 2.0
mike deploy 2.0 latest --update-aliases

# Set default version
mike set-default latest
```

## Version Naming Scheme

Documentation versions will follow these conventions:

| SDK Version | Doc Version | Alias | Description |
|-------------|-------------|-------|-------------|
| 0.1.x | 0.1 | - | Patch releases share doc version |
| 0.2.x | 0.2 | latest | Latest stable release |
| 1.0.x | 1.0 | latest, stable | Major version |
| main branch | dev | - | Development (unreleased) |

### Rationale

- **Major.Minor only**: Patch releases (0.1.0 → 0.1.1) typically don't change APIs, so they share docs
- **Aliases**: `latest` always points to the newest stable version
- **Dev docs**: Available for those who want to see upcoming features

## Deployment Workflow

### Current Workflow (Single Version)

```yaml
# .github/workflows/docs.yml
on:
  push:
    branches: [master, main]

steps:
  - mkdocs build
  - deploy to gh-pages
```

### Future Workflow (Multi-Version with mike)

```yaml
# Will be implemented in v0.2.0
on:
  push:
    tags: ['v*']  # Trigger on version tags

steps:
  - Install mike
  - Extract version from tag (v1.2.3 → 1.2)
  - mike deploy <version> latest
  - mike set-default latest
```

## Version Switcher

When we implement versioning, the documentation site will have a version dropdown:

```
┌─────────────────────────────┐
│ Ainalyn SDK Documentation   │
│                             │
│ Version: 1.0 ▼              │
│   - dev (unreleased)        │
│   - 1.0 (latest)            │
│   - 0.2                     │
│   - 0.1                     │
└─────────────────────────────┘
```

## Implementation Timeline

| Milestone | Action | Timeline |
|-----------|--------|----------|
| v0.1.0 | Single-version docs (current) | ✅ Completed |
| v0.2.0 | Add mike for multi-version | Planned |
| v1.0.0 | Full version switcher UI | Planned |

## Configuration (Future)

### mkdocs.yml updates needed

```yaml
# Add version provider
extra:
  version:
    provider: mike
```

### GitHub Actions updates needed

```yaml
# Install mike
- name: Install mike
  run: pip install mike

# Deploy with version
- name: Deploy docs
  run: |
    VERSION=$(echo ${GITHUB_REF#refs/tags/v} | cut -d. -f1,2)
    mike deploy $VERSION latest --push --update-aliases
```

## References

- [Material for MkDocs Versioning](https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/) - Official versioning guide
- [mike Documentation](https://github.com/jimporter/mike) - Version management tool for MkDocs

## Questions?

- Why not version from the start? **Answer**: Keep it simple until we have multiple versions
- Why mike? **Answer**: Recommended by Material for MkDocs, used by successful projects
- What about old versions? **Answer**: We'll maintain docs for the last 2 major versions

---

**Status**: Single-version deployment (v0.1.0) ✅
**Next**: Implement mike when releasing v0.2.0
