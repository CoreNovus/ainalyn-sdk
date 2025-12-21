# Installation

This guide will help you install the Ainalyn SDK and set up your development environment.

## Requirements

- **Python**: 3.11 or higher (3.11, 3.12, 3.13 supported)
- **pip**: Latest version recommended
- **Operating System**: Cross-platform (Windows, macOS, Linux)

## Installation Methods

### Install from PyPI (Recommended)

Install the latest stable release from PyPI:

```bash
pip install ainalyn-sdk
```

### Install from Source

For development or to use the latest unreleased features:

```bash
# Clone the repository
git clone https://github.com/ainalyn/ainalyn-sdk.git
cd ainalyn-sdk

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

### Install with Optional Dependencies

The SDK provides optional dependency groups for different use cases:

```bash
# Install with documentation tools
pip install "ainalyn-sdk[docs]"

# Install with testing tools
pip install "ainalyn-sdk[test]"

# Install with all development dependencies
pip install "ainalyn-sdk[dev]"

# Install everything (dev + docs)
pip install "ainalyn-sdk[all]"
```

## Verify Installation

After installation, verify that the SDK is properly installed:

### Check Version

```bash
ainalyn --version
```

Expected output:
```
ainalyn-sdk 0.1.0
```

### Check Python Import

```python
python -c "import ainalyn; print(ainalyn.__version__)"
```

Expected output:
```
0.1.0
```

### Verify CLI Commands

The SDK provides a command-line interface (CLI) for common tasks:

```bash
# Show available commands
ainalyn --help
```

Expected output:
```
Usage: ainalyn [OPTIONS] COMMAND [ARGS]...

  Ainalyn SDK - Agent Definition Compiler

Commands:
  validate    Validate an agent definition file
  compile     Compile agent definition to YAML
  version     Show SDK version
```

## Development Setup (For Contributors)

If you plan to contribute to the Ainalyn SDK, follow these additional setup steps:

### 1. Install Pre-commit Hooks

Pre-commit hooks ensure code quality before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

### 2. Verify Development Tools

Check that all development tools are available:

```bash
# Linting and formatting
ruff --version

# Type checking
mypy --version

# Testing
pytest --version
```

### 3. Run Initial Tests

Ensure everything is working:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ainalyn --cov-report=term-missing
```

Expected: All tests should pass with ≥85% coverage.

## IDE Setup

### Visual Studio Code

Recommended extensions for VS Code:

- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Ruff** (Astral Software)
- **Python Type Hint** (Robert Craigie)

Recommended settings (`.vscode/settings.json`):

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll": true
    }
  },
  "python.analysis.typeCheckingMode": "strict",
  "python.testing.pytestEnabled": true
}
```

### PyCharm

1. Configure interpreter: **File → Settings → Project → Python Interpreter**
2. Enable type checking: **Settings → Editor → Inspections → Python → Type Checker**
3. Configure Ruff: **Settings → Tools → External Tools** (add Ruff)

## Troubleshooting

### Python Version Issues

If you see errors about Python version:

```bash
# Check your Python version
python --version

# If < 3.11, install a newer Python version
# On Ubuntu/Debian:
sudo apt install python3.11

# On macOS with Homebrew:
brew install python@3.11

# On Windows: Download from python.org
```

### Permission Errors

If you encounter permission errors during installation:

```bash
# Use --user flag
pip install --user ainalyn-sdk

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ainalyn-sdk
```

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Ensure ainalyn is installed
pip list | grep ainalyn

# Reinstall if needed
pip uninstall ainalyn-sdk
pip install ainalyn-sdk
```

### Development Dependencies Not Found

If development tools are missing:

```bash
# Reinstall with dev dependencies
pip install "ainalyn-sdk[dev]"

# Or install individually
pip install pytest mypy ruff pre-commit
```

## Virtual Environment Best Practices

We **strongly recommend** using virtual environments:

### Using venv (built-in)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install SDK
pip install ainalyn-sdk

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create environment
conda create -n ainalyn python=3.11

# Activate
conda activate ainalyn

# Install SDK
pip install ainalyn-sdk
```

### Using poetry

```bash
# Initialize project
poetry init

# Add SDK
poetry add ainalyn-sdk

# Install
poetry install
```

## Next Steps

Now that you have the SDK installed:

1. **[Quickstart Guide](quickstart.md)** - Build a simple agent in 5 minutes
2. **[Your First Agent](your-first-agent.md)** - Detailed walkthrough of agent creation
3. **[Platform Boundaries](../concepts/platform-boundaries.md)** - Understand SDK limitations

## Getting Help

- **Installation issues**: [GitHub Issues](https://github.com/ainalyn/ainalyn-sdk/issues)
- **General questions**: [GitHub Discussions](https://github.com/ainalyn/ainalyn-sdk/discussions)
- **Email support**: dev@ainalyn.io
