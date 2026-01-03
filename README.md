# Ainalyn SDK

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-175%20passed-success)](https://github.com/CoreNovus/ainalyn-sdk)
[![Type Coverage](https://img.shields.io/badge/type%20coverage-100%25-success)](https://github.com/CoreNovus/ainalyn-sdk)

**Official Python SDK for Building Task-Oriented Agents on Ainalyn Platform**

The Ainalyn SDK is a dual-purpose toolkit that enables developers to:
1. **Define & Compile** agents using type-safe Python builders
2. **Execute** ATOMIC agents as AWS Lambda functions with built-in runtime support

---

## 📋 Table of Contents

- [What is Ainalyn SDK?](#what-is-ainalyn-sdk)
- [Key Features](#key-features)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Core Concepts](#core-concepts)
- [Development Paths](#development-paths)
- [Complete Examples](#complete-examples)
- [CLI Reference](#cli-reference)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)
- [Contributing](#contributing)

---

## What is Ainalyn SDK?

Ainalyn SDK is the **official development kit** for creating task-oriented agents on the Ainalyn Platform. It provides:

- **Type-Safe Builder API** - Define agents with full IDE autocomplete and compile-time validation
- **Comprehensive Validation** - Schema validation, static analysis, and platform review gate checks
- **Runtime Wrapper** - Deploy code-first agents as AWS Lambda functions with automatic SYNC/ASYNC handling
- **CLI Tools** - Validate and compile agents from the command line
- **Production Ready** - 175 tests, >85% coverage, strict mypy type checking

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Ainalyn SDK                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐         ┌─────────────────┐      │
│  │  Builder API    │         │  Runtime        │      │
│  │  (Compiler)     │         │  (Executor)     │      │
│  ├─────────────────┤         ├─────────────────┤      │
│  │ • AgentBuilder  │         │ • @agent.atomic │      │
│  │ • Validators    │         │ • SYNC/ASYNC    │      │
│  │ • YAML Exporter │         │ • State Report  │      │
│  └─────────────────┘         └─────────────────┘      │
│           │                           │                │
│           ▼                           ▼                │
│    agent.yaml ──────────► Platform Core ◄──── Lambda  │
└─────────────────────────────────────────────────────────┘
```

---

## Key Features

### 🎯 Dual Development Paths

**COMPOSITE Agents (Graph-First)**
- Build workflows using visual node-based graphs
- No code required - pure configuration
- Executed by Platform Core's Graph Executor
- Perfect for: Data pipelines, multi-step processes, orchestration

**ATOMIC Agents (Code-First)**
- Write Python functions with custom business logic
- Full control over implementation
- Executed by SDK Runtime in AWS Lambda
- Perfect for: Custom algorithms, API integrations, data transformations

### ✅ Comprehensive Validation

- **Schema Validation** - Ensures structural correctness
- **Static Analysis** - Detects circular dependencies, dead-end nodes
- **Review Gate Validation** - Platform Core compliance checks
- **Type Safety** - 100% strict mypy coverage

### 🚀 Production Features

- **SYNC/ASYNC Modes** - Automatic routing for short (<29s) and long-running tasks
- **State Management** - Built-in DynamoDB integration for async executions
- **Error Handling** - Standardized error format with retry hints
- **Idempotency** - Safe retry handling for failed executions

---

## Quick Start (5 Minutes)

### Installation

```bash
# Core SDK (for agent definition and compilation)
pip install ainalyn-sdk

# With runtime support (for ATOMIC agents)
pip install ainalyn-sdk boto3
```

**Requirements:**
- Python 3.11, 3.12, or 3.13
- PyYAML >= 6.0
- boto3 (optional, for ATOMIC runtime)

### Your First COMPOSITE Agent

**Step 1: Define your agent**

Create `my_agent.py`:

```python
from ainalyn import (
    AgentBuilder,
    AgentType,
    WorkflowBuilder,
    NodeBuilder,
    ModuleBuilder,
    CompletionCriteria,
)

# 1. Define reusable modules (capabilities)
data_fetcher = ModuleBuilder("http-fetch") \
    .description("Fetches data from HTTP endpoints") \
    .build()

# 2. Build workflow with nodes
workflow = WorkflowBuilder("main") \
    .description("Fetch and process data") \
    .add_node(
        NodeBuilder("fetch")
        .description("Fetch data from API")
        .uses_module("http-fetch")
        .outputs("raw_data")
        .build()
    ) \
    .entry_node("fetch") \
    .build()

# 3. Create agent definition
agent = AgentBuilder("data-processor") \
    .version("1.0.0") \
    .description("Processes data from external APIs") \
    .agent_type(AgentType.COMPOSITE) \
    .task_goal("Fetch and validate data from HTTP endpoints") \
    .completion_criteria(
        CompletionCriteria(
            success="Data fetched and validated successfully",
            failure="HTTP error or validation failed"
        )
    ) \
    .input_schema({
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"}
        },
        "required": ["url"]
    }) \
    .output_schema({
        "type": "object",
        "properties": {
            "data": {"type": "object"},
            "status": {"type": "string"}
        }
    }) \
    .add_module(data_fetcher) \
    .add_workflow(workflow) \
    .build()
```

**Step 2: Compile to YAML**

```bash
# Using CLI
ainalyn compile my_agent.py --output agent.yaml

# Or using Python API
```

```python
from ainalyn import compile_agent

result = compile_agent(agent, output_path="agent.yaml")
if result.is_valid:
    print(f"✓ Success: {result.file_path}")
    print(f"  YAML size: {len(result.yaml_content)} bytes")
else:
    print("✗ Validation failed:")
    for error in result.validation_result.errors:
        print(f"  - {error.code}: {error.message}")
```

**Step 3: Review generated YAML**

```yaml
# agent.yaml
name: data-processor
version: 1.0.0
description: Processes data from external APIs
agent_type: COMPOSITE
task_goal: Fetch and validate data from HTTP endpoints
completion_criteria:
  success: Data fetched and validated successfully
  failure: HTTP error or validation failed
input_schema:
  type: object
  properties:
    url:
      type: string
      format: uri
  required:
    - url
output_schema:
  type: object
  properties:
    data:
      type: object
    status:
      type: string
workflows:
  - name: main
    description: Fetch and process data
    entry_node: fetch
    nodes:
      - name: fetch
        description: Fetch data from API
        type: module
        reference: http-fetch
        outputs:
          - raw_data
modules:
  - name: http-fetch
    description: Fetches data from HTTP endpoints
```

### Your First ATOMIC Agent

**Step 1: Write your handler**

Create `pdf_parser.py`:

```python
from ainalyn.runtime import agent
import PyPDF2
import requests
from io import BytesIO

@agent.atomic(name="pdf-parser", version="1.0.0")
def parse_pdf(input_data: dict) -> dict:
    """
    Extract text from PDF files.

    Input: {"file_url": "https://example.com/document.pdf"}
    Output: {"text": "...", "page_count": 10}
    """
    # Get PDF from URL
    file_url = input_data["file_url"]
    response = requests.get(file_url)
    pdf_file = BytesIO(response.content)

    # Extract text
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    return {
        "text": text,
        "page_count": len(reader.pages),
        "file_url": file_url
    }
```

**Step 2: Create agent definition**

Create `pdf_parser_definition.py`:

```python
from ainalyn import AgentBuilder, AgentType, CompletionCriteria, compile_agent

agent = AgentBuilder("pdf-parser") \
    .version("1.0.0") \
    .description("Extracts text from PDF documents") \
    .agent_type(AgentType.ATOMIC) \
    .task_goal("Extract all text content from PDF files") \
    .completion_criteria(
        CompletionCriteria(
            success="Text extracted successfully from all pages",
            failure="PDF corrupted, password-protected, or invalid format"
        )
    ) \
    .input_schema({
        "type": "object",
        "properties": {
            "file_url": {"type": "string", "format": "uri"}
        },
        "required": ["file_url"]
    }) \
    .output_schema({
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "page_count": {"type": "integer"},
            "file_url": {"type": "string"}
        }
    }) \
    .build()

# Compile
compile_agent(agent, output_path="pdf-parser.yaml")
```

**Step 3: Deploy to AWS Lambda**

```bash
# Package your code
zip -r function.zip pdf_parser.py requirements.txt

# Deploy using AWS CLI (example)
aws lambda create-function \
  --function-name pdf-parser \
  --runtime python3.11 \
  --handler pdf_parser.parse_pdf \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT:role/lambda-role
```

---

## Core Concepts

### Agent Types

| Type | Description | Execution | Use Cases |
|------|-------------|-----------|-----------|
| **COMPOSITE** | Graph-based workflow definition | Platform Core Graph Executor | Data pipelines, orchestration, multi-step processes |
| **ATOMIC** | Code-first Python function | SDK Runtime (AWS Lambda) | Custom algorithms, API integrations, transformations |

### Execution Modes

**SYNC Mode (Fast Route)**
- Tasks completing in < 29 seconds
- Direct Lambda invocation (RequestResponse)
- Result returned immediately
- Platform Core waits for response

**ASYNC Mode (Heavy Route)**
- Long-running tasks (> 29 seconds)
- Event-based Lambda invocation
- SDK writes result to DynamoDB
- Platform Core polls for completion

### Review Gates

All agents must pass Platform Core's review gates:

**Gate 1: Contract Completeness**
- ✅ `task_goal` - What does this agent do?
- ✅ `completion_criteria` - Success/failure conditions
- ✅ `input_schema` - Expected input structure
- ✅ `output_schema` - Expected output structure

**Gate 2: No Shadow Runtime**
- ❌ No infinite loops or unbounded iterations
- ❌ No circular dependencies

**Gate 4: No Billing Authority**
- ❌ SDK cannot calculate fees or make billing decisions

**Gate 5: EIP Dependencies**
- ✅ Declare all EIP module dependencies

---

## Development Paths

### Path 1: COMPOSITE Agents (Recommended for Beginners)

**When to use:**
- Building data pipelines
- Orchestrating multiple steps
- No custom code required
- Leveraging existing platform modules

**Example: Multi-Step Data Pipeline**

```python
from ainalyn import (
    AgentBuilder, WorkflowBuilder, NodeBuilder,
    ModuleBuilder, PromptBuilder, AgentType, CompletionCriteria
)

# Define modules
http_fetch = ModuleBuilder("http-fetch").description("HTTP client").build()
json_parser = ModuleBuilder("json-parse").description("JSON parser").build()

# Define prompts
analyzer = PromptBuilder("analyze-data") \
    .description("Analyze structured data") \
    .template("Analyze this data and extract key insights: {{data}}") \
    .variables("data") \
    .build()

# Build workflow: fetch → parse → analyze
workflow = WorkflowBuilder("data-pipeline") \
    .description("Fetch, parse, and analyze data") \
    .add_node(
        NodeBuilder("fetch")
        .description("Fetch from API")
        .uses_module("http-fetch")
        .outputs("raw_response")
        .next_nodes("parse")
        .build()
    ) \
    .add_node(
        NodeBuilder("parse")
        .description("Parse JSON response")
        .uses_module("json-parse")
        .inputs("raw_response")
        .outputs("structured_data")
        .next_nodes("analyze")
        .build()
    ) \
    .add_node(
        NodeBuilder("analyze")
        .description("Analyze data with LLM")
        .uses_prompt("analyze-data")
        .inputs("structured_data")
        .outputs("insights")
        .build()
    ) \
    .entry_node("fetch") \
    .build()

# Create agent
agent = AgentBuilder("data-analyzer") \
    .version("1.0.0") \
    .description("Fetches, parses, and analyzes data") \
    .agent_type(AgentType.COMPOSITE) \
    .task_goal("Extract insights from external API data") \
    .completion_criteria(
        CompletionCriteria(
            success="Data analyzed and insights extracted",
            failure="API error, invalid JSON, or analysis failed"
        )
    ) \
    .input_schema({
        "type": "object",
        "properties": {
            "api_url": {"type": "string"},
            "api_key": {"type": "string"}
        },
        "required": ["api_url"]
    }) \
    .output_schema({
        "type": "object",
        "properties": {
            "insights": {"type": "string"},
            "data_quality": {"type": "string"}
        }
    }) \
    .add_module(http_fetch) \
    .add_module(json_parser) \
    .add_prompt(analyzer) \
    .add_workflow(workflow) \
    .build()
```

### Path 2: ATOMIC Agents (For Custom Logic)

**When to use:**
- Custom algorithms or business logic
- Third-party API integrations
- Data transformations
- Performance-critical operations

**Example: Real-Time Price Monitor**

```python
from ainalyn.runtime import agent
from ainalyn.runtime.errors import HandlerError, InputValidationError
import requests
from datetime import datetime

@agent.atomic(name="price-monitor", version="1.0.0")
def monitor_price(input_data: dict) -> dict:
    """
    Monitor cryptocurrency prices in real-time.

    Input:
        {
            "symbol": "BTC",
            "threshold": 50000,
            "check_type": "above" or "below"
        }

    Output:
        {
            "alert": true/false,
            "current_price": 51234.56,
            "threshold": 50000,
            "timestamp": "2026-01-03T10:30:00Z"
        }
    """
    # Validate inputs
    symbol = input_data.get("symbol")
    threshold = input_data.get("threshold")
    check_type = input_data.get("check_type", "above")

    if not symbol or not threshold:
        raise InputValidationError(
            message="Missing required fields: symbol and threshold",
            details={"received": input_data}
        )

    # Fetch current price (example API)
    try:
        response = requests.get(
            f"https://api.exchange.com/price/{symbol}",
            timeout=10
        )
        response.raise_for_status()
        price_data = response.json()
        current_price = price_data["price"]
    except requests.RequestException as e:
        raise HandlerError(
            message=f"Failed to fetch price for {symbol}",
            details={"error": str(e), "symbol": symbol},
            retryable=True  # Platform may retry
        )

    # Check threshold
    if check_type == "above":
        alert = current_price > threshold
    else:
        alert = current_price < threshold

    return {
        "alert": alert,
        "current_price": current_price,
        "threshold": threshold,
        "check_type": check_type,
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

**Corresponding definition:**

```python
from ainalyn import AgentBuilder, AgentType, CompletionCriteria

agent = AgentBuilder("price-monitor") \
    .version("1.0.0") \
    .description("Real-time cryptocurrency price monitoring") \
    .agent_type(AgentType.ATOMIC) \
    .task_goal("Monitor crypto prices and alert on threshold crossings") \
    .completion_criteria(
        CompletionCriteria(
            success="Price checked and alert decision made",
            failure="API unavailable or invalid symbol"
        )
    ) \
    .input_schema({
        "type": "object",
        "properties": {
            "symbol": {"type": "string", "pattern": "^[A-Z]{3,10}$"},
            "threshold": {"type": "number", "minimum": 0},
            "check_type": {"type": "string", "enum": ["above", "below"]}
        },
        "required": ["symbol", "threshold"]
    }) \
    .output_schema({
        "type": "object",
        "properties": {
            "alert": {"type": "boolean"},
            "current_price": {"type": "number"},
            "threshold": {"type": "number"},
            "symbol": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"}
        }
    }) \
    .build()
```

---

## Complete Examples

### Example 1: Weather Alert Agent (COMPOSITE)

A workflow-based agent that fetches weather data and sends alerts.

See: [`examples/weather_alert_agent.py`](examples/weather_alert_agent.py)

### Example 2: Document Summarizer (ATOMIC)

An AI-powered document summarization service.

See: [`examples/document_summarizer.py`](examples/document_summarizer.py)

### Example 3: Meeting Transcriber (COMPOSITE)

Multi-step workflow for transcribing and analyzing meetings.

See: [`examples/meeting_transcriber_agent.py`](examples/meeting_transcriber_agent.py)

### Example 4: Price Monitor (ATOMIC)

Real-time price monitoring with custom business logic.

See: [`examples/price_monitor_agent.py`](examples/price_monitor_agent.py)

---

## CLI Reference

### Installation Check

```bash
# Check SDK version
ainalyn --version

# Verify installation
python -c "import ainalyn; print(ainalyn.__version__)"
```

### Validate Agent

```bash
# Validate a Python file containing AgentDefinition
ainalyn validate my_agent.py

# Example output:
# ✓ Validation passed
#   - Schema validation: OK
#   - Review gates: OK
#   - Static analysis: OK
```

### Compile Agent

```bash
# Compile to YAML
ainalyn compile my_agent.py --output agent.yaml

# Example output:
# ✓ Compiled successfully
#   Output: agent.yaml (1,234 bytes)
#   Agent: data-processor v1.0.0
```

### Advanced Usage

```python
# Programmatic usage with detailed error handling
from ainalyn import validate, compile_agent
from ainalyn.domain.entities import AgentDefinition

# Load your agent
agent: AgentDefinition = ...

# Validate first
result = validate(agent)
if not result.is_valid:
    print("Validation errors:")
    for error in result.errors:
        print(f"  [{error.severity}] {error.code}")
        print(f"    Path: {error.path}")
        print(f"    Message: {error.message}")
    exit(1)

# Compile if valid
compilation = compile_agent(agent, output_path="agent.yaml")
print(f"✓ Compiled: {compilation.file_path}")
```

---

## Troubleshooting

### Common Issues

#### 1. Import Error: `ModuleNotFoundError: No module named 'ainalyn'`

**Solution:**
```bash
# Ensure SDK is installed
pip install ainalyn-sdk

# Verify installation
python -c "import ainalyn"
```

#### 2. Validation Error: `GATE1_MISSING_TASK_GOAL`

**Cause:** Missing required v0.2 fields.

**Solution:**
```python
agent = AgentBuilder("my-agent") \
    .version("1.0.0") \
    .description("...") \
    .task_goal("What does this agent accomplish?")  # ← Add this
    .completion_criteria(                           # ← Add this
        CompletionCriteria(
            success="When is it successful?",
            failure="When does it fail?"
        )
    ) \
    .input_schema({"type": "object", ...})         # ← Add this
    .output_schema({"type": "object", ...})        # ← Add this
    .build()
```

#### 3. Runtime Error: `boto3 is required for ASYNC mode`

**Cause:** ATOMIC agent in ASYNC mode needs boto3.

**Solution:**
```bash
pip install boto3
```

#### 4. Type Error: `AgentDefinition.__init__() missing 1 required positional argument: 'agent_type'`

**Cause:** v0.2 requires explicit agent type.

**Solution:**
```python
from ainalyn import AgentType

agent = AgentBuilder("my-agent") \
    .agent_type(AgentType.COMPOSITE)  # ← Add this
    # or
    .agent_type(AgentType.ATOMIC)     # ← For code-first agents
    .build()
```

#### 5. Workflow Validation Error: `Circular dependency detected`

**Cause:** Nodes reference each other in a loop.

**Solution:**
```python
# ❌ Bad: A → B → A (circular)
NodeBuilder("A").next_nodes("B").build()
NodeBuilder("B").next_nodes("A").build()

# ✅ Good: A → B → C (linear)
NodeBuilder("A").next_nodes("B").build()
NodeBuilder("B").next_nodes("C").build()
NodeBuilder("C").build()
```

#### 6. CLI Error: `agent` or `definition` variable not found

**Cause:** Python file doesn't export the right variable.

**Solution:**
```python
# In your agent file, ensure you have:
agent = AgentBuilder(...).build()  # ← Must be named 'agent' or 'definition'
```

### Getting Help

- **Documentation**: [docs.ainalyn.corenovus.com](http://docs.ainalyn.corenovus.com/)
- **GitHub Issues**: [github.com/CoreNovus/ainalyn-sdk/issues](https://github.com/CoreNovus/ainalyn-sdk/issues)
- **Stack Overflow**: Tag with `ainalyn-sdk`
- **Discord Community**: [discord.gg/ainalyn](https://discord.gg/ainalyn)

---

## API Reference

### High-Level Functions

```python
from ainalyn import validate, export_yaml, compile_agent

# Validate an agent definition
result: ValidationResult = validate(agent)
# Returns: ValidationResult(is_valid, errors, warnings)

# Export to YAML string
yaml_str: str = export_yaml(agent)
# Returns: YAML string (no validation)

# Compile with validation
result: CompilationResult = compile_agent(agent, output_path="agent.yaml")
# Returns: CompilationResult(is_successful, yaml_content, file_path, validation_result)
```

### Builder API

```python
from ainalyn import (
    AgentBuilder,        # Main agent builder
    WorkflowBuilder,     # Workflow definition
    NodeBuilder,         # Workflow nodes
    ModuleBuilder,       # Reusable modules
    PromptBuilder,       # LLM prompts
    ToolBuilder,         # External tools
    AgentType,           # ATOMIC | COMPOSITE
    CompletionCriteria,  # Success/failure conditions
)

# All builders support method chaining
agent = AgentBuilder("name") \
    .version("1.0.0") \
    .description("...") \
    .build()
```

### Runtime API (ATOMIC Agents)

```python
from ainalyn.runtime import agent
from ainalyn.runtime.errors import (
    HandlerError,            # Base error class
    InputValidationError,    # Invalid input
    ExternalServiceError,    # Third-party API failure
    TimeoutError,            # Operation timeout
)

# Decorate your handler
@agent.atomic(name="my-agent", version="1.0.0")
def handler(input_data: dict) -> dict:
    # Your logic here
    return {"result": "..."}

# Error handling
try:
    result = call_external_api()
except Exception as e:
    raise ExternalServiceError(
        service="api.example.com",
        message="API call failed",
        retryable=True  # Platform may retry
    )
```

### Domain Entities

```python
from ainalyn.domain.entities import (
    AgentDefinition,      # Complete agent definition
    Workflow,             # Workflow entity
    Node,                 # Workflow node
    Module,               # Reusable module
    Prompt,               # LLM prompt
    Tool,                 # External tool
    NodeType,             # MODULE | PROMPT | TOOL | WORKFLOW_REF
)
```

---

## Requirements

**Python Version:**
- Python 3.11, 3.12, or 3.13

**Core Dependencies:**
- PyYAML >= 6.0 (YAML serialization)

**Optional Dependencies:**
- boto3 (for ATOMIC agent runtime with ASYNC mode)

**Development Dependencies:**
- pytest >= 7.4.0 (testing)
- mypy >= 1.7.0 (type checking)
- ruff >= 0.1.8 (linting & formatting)

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process
- Platform boundary rules

**Quick Start for Contributors:**

```bash
# Clone repository
git clone https://github.com/CoreNovus/ainalyn-sdk.git
cd ainalyn-sdk

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checker
mypy ainalyn/

# Run linter
ruff check ainalyn/ tests/
```

**For Newcomers:**
Look for issues labeled [`good first issue`](https://github.com/CoreNovus/ainalyn-sdk/labels/good%20first%20issue).

---

## License

[MIT License](LICENSE) - see LICENSE file for details.

Copyright (c) 2024-2026 CoreNovus Team

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

**Current Version:** 0.1.0-alpha.5

**Recent Changes:**
- ✅ Full v0.2 spec compliance (Worker Protocol)
- ✅ Review Gate 1 validation
- ✅ 175 tests with 100% pass rate
- ✅ SYNC/ASYNC runtime support
- ✅ Comprehensive documentation

---

## Support & Resources

- **📚 Documentation**: [docs.ainalyn.corenovus.com](http://docs.ainalyn.corenovus.com/)
- **🐛 Report Issues**: [GitHub Issues](https://github.com/CoreNovus/ainalyn-sdk/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/CoreNovus/ainalyn-sdk/discussions)
- **📧 Email**: dev@ainalyn.io
- **💭 Discord**: [discord.gg/ainalyn](https://discord.gg/ainalyn)

---

**Built with ❤️ by the CoreNovus Team**

[Website](https://ainalyn.io) • [Platform](https://platform.ainalyn.io) • [Blog](https://blog.ainalyn.io)
