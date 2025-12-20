# My Project

Project description here.

## Getting Started

### Prerequisites

- Python 3.11+

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/macOS:
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

## Development

```bash
# Run linting
make lint

# Run tests
make test

# Format code
make format

# Type checking
make type-check
```

## License

MIT
