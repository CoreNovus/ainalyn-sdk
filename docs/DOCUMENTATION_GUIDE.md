# Documentation Guide for New Contributors

Welcome! This guide helps you navigate the Ainalyn SDK documentation and understand how to contribute.

## Documentation Structure

Our documentation is organized into clear sections:

### For Users (Learning to use the SDK)

```
docs/
├── index.md                    # Start here!
├── getting-started/            # First steps
│   ├── installation.md        # How to install
│   ├── quickstart.md          # 5-minute tutorial
│   └── your-first-agent.md    # Detailed walkthrough
├── concepts/                   # Understanding the SDK
│   ├── platform-boundaries.md # What SDK can/cannot do
│   ├── compiler-not-runtime.md# SDK vs Platform
│   ├── architecture-overview.md# How SDK is built
│   └── agent-definition.md    # What you're building
└── troubleshooting.md         # Common problems
```

### For Contributors (Helping improve the SDK)

```
CONTRIBUTING.md                 # Start here for contributing!
docs/
├── contributor-guide/          # Developer documentation
│   ├── architecture/          # Technical architecture
│   └── development-setup.md   # Setting up dev environment
└── changelog.md               # Version history
```

## Quick Links for Common Tasks

### I want to...

**Learn the SDK**
1. Start: [Installation](getting-started/installation.md)
2. Then: [Quickstart](getting-started/quickstart.md)
3. Build: [Your First Agent](getting-started/your-first-agent.md)

**Understand SDK limits**
- Read: [Platform Boundaries](concepts/platform-boundaries.md)
- Key: SDK is a compiler, not runtime

**Fix something that's broken**
- Check: [Troubleshooting](troubleshooting.md)
- Still stuck? [Open an issue](https://github.com/ainalyn/ainalyn-sdk/issues)

**Contribute code or docs**
1. Read: [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Pick: Look for `good first issue` labels
3. Setup: Follow development setup guide
4. Submit: Create a pull request

## Documentation Files Location

All documentation source files are in the `docs/` directory:

- **Markdown files** (`.md`): Human-written documentation
- **Built site**: Generated in `site/` when you run `mkdocs build`
- **Configuration**: `mkdocs.yml` at repository root

## Building Documentation Locally

To preview documentation on your machine:

```bash
# Install dependencies (in virtual environment)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
pip install ".[docs]"

# Build and serve
mkdocs serve

# Open browser to http://127.0.0.1:8000
```

The documentation will auto-reload when you edit files.

## Writing Documentation

### Style Guidelines

**Be clear and concise**
- Write for beginners
- Use simple English
- Avoid jargon when possible
- Explain technical terms when first used

**Use examples**
- Show code examples
- Include expected output
- Demonstrate common patterns

**Structure well**
- Use headings (H2, H3, H4)
- Use lists for multiple items
- Use tables for comparisons
- Use code blocks with language tags

### Example Documentation Template

```markdown
# Page Title

Brief introduction (1-2 sentences).

## What This Is

Explain the concept or feature.

## Why It Matters

Explain the value or use case.

## How to Use It

Provide step-by-step instructions with code examples.

```python
# Example code
from ainalyn import AgentBuilder

agent = AgentBuilder("MyAgent").build()
```

## Common Patterns

Show typical use cases.

## Troubleshooting

List common issues and solutions.
```

### Markdown Features

We use Material for MkDocs with these features:

**Admonitions** (callouts):
```markdown
!!! note
    This is a note.

!!! warning
    This is a warning.

!!! danger
    Critical information.
```

**Code blocks**:
````markdown
```python
# Python code with syntax highlighting
agent = AgentBuilder("MyAgent").build()
```
````

**Tables**:
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

## Updating Documentation

### For Small Changes

1. Edit the `.md` file in `docs/`
2. Preview with `mkdocs serve`
3. Commit and push

### For New Pages

1. Create `.md` file in appropriate `docs/` subdirectory
2. Add to `mkdocs.yml` navigation section
3. Preview to ensure it appears correctly
4. Commit and push

### For API Documentation

API documentation uses `mkdocstrings` to auto-generate from Python docstrings:

1. Write good docstrings in source code (Google style)
2. Create page that references the code
3. The tool extracts and formats automatically

Example:
```markdown
# AgentBuilder API

::: ainalyn.adapters.primary.builders.AgentBuilder
```

## Documentation Deployment

Documentation is automatically deployed when changes are merged to `master`:

1. GitHub Actions triggers on push to master
2. MkDocs builds the documentation
3. Result is published to GitHub Pages
4. Available at https://docs.ainalyn.io/sdk

You don't need to deploy manually.

## Getting Help

**Documentation issues**
- Check [troubleshooting guide](troubleshooting.md)
- Open an issue with `documentation` label
- Ask in GitHub Discussions

**Contributing questions**
- Read [CONTRIBUTING.md](../CONTRIBUTING.md)
- Check existing issues/PRs for examples
- Ask in Discussions if unclear

## Best Practices

**When writing documentation:**
- [ ] Test all code examples
- [ ] Check for broken links
- [ ] Preview locally before committing
- [ ] Keep language simple and clear
- [ ] Include troubleshooting tips

**When reviewing documentation PRs:**
- [ ] Check for accuracy
- [ ] Verify examples work
- [ ] Ensure consistent style
- [ ] Test all links
- [ ] Preview the built site

## Common Documentation Tasks

### Adding a New Tutorial

1. Create file: `docs/getting-started/new-tutorial.md`
2. Add to `mkdocs.yml` under "Getting Started"
3. Write step-by-step content
4. Add code examples
5. Test examples work
6. Preview and submit PR

### Fixing a Typo

1. Find the `.md` file in `docs/`
2. Edit directly on GitHub or locally
3. Submit PR with fix
4. Label: `documentation`

### Improving an Example

1. Locate example in documentation
2. Update with better code or explanation
3. Test the code works
4. Submit PR

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Markdown Guide](https://www.markdownguide.org/)

---

**Ready to contribute?** Start with [CONTRIBUTING.md](../CONTRIBUTING.md)!

**Questions?** Open a [GitHub Discussion](https://github.com/ainalyn/ainalyn-sdk/discussions)!
