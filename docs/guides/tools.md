# Tools

How to define external tool interfaces for your agents.

## What is a Tool?

A tool represents an external capability that your agent can invoke. It defines:

- **What it does** (description)
- **What input it expects** (input schema)
- **What output it produces** (output schema)

**Important:** The SDK only defines the tool's interface contract. The platform provides the actual implementation.

## Creating a Tool

```python
from ainalyn import ToolBuilder

tool = (
    ToolBuilder("web-search")
    .description("Searches the web for information")
    .input_schema({
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer", "default": 10}
        },
        "required": ["query"]
    })
    .output_schema({
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "url": {"type": "string"},
                        "snippet": {"type": "string"}
                    }
                }
            }
        }
    })
    .build()
)
```

## Using Tools in Workflows

**Step 1: Define the tool**

```python
search_tool = (
    ToolBuilder("web-search")
    .description("Searches the web")
    .input_schema({...})
    .output_schema({...})
    .build()
)
```

**Step 2: Add tool to agent**

```python
agent = (
    AgentBuilder("research-agent")
    .version("1.0.0")
    .add_tool(search_tool)  # Register tool
    .add_workflow(workflow)
    .build()
)
```

**Step 3: Reference in node**

```python
from ainalyn import NodeBuilder, NodeType

node = (
    NodeBuilder("search")
    .description("Search for information")
    .node_type(NodeType.TOOL)
    .reference("web-search")  # References the tool
    .inputs(["query"])
    .outputs(["results"])
    .build()
)
```

## JSON Schema

Tools use JSON Schema to define input/output contracts (same as modules).

**Basic example:**

```python
input_schema = {
    "type": "object",
    "properties": {
        "path": {"type": "string"},
        "content": {"type": "string"}
    },
    "required": ["path", "content"]
}

output_schema = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "bytes_written": {"type": "integer"}
    }
}
```

See [Modules Guide](modules.md#json-schema) for detailed schema examples.

## Common Tool Patterns

### Web Search

```python
search = (
    ToolBuilder("web-search")
    .description("Searches the web for information")
    .input_schema({
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "language": {"type": "string", "default": "en"},
            "safe_search": {"type": "boolean", "default": True}
        },
        "required": ["query"]
    })
    .output_schema({
        "type": "object",
        "properties": {
            "results": {"type": "array", "items": {"type": "object"}},
            "total_count": {"type": "integer"}
        }
    })
    .build()
)
```

### Database Query

```python
db_query = (
    ToolBuilder("database-query")
    .description("Executes SQL queries on database")
    .input_schema({
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "parameters": {"type": "array"},
            "timeout": {"type": "integer", "default": 30}
        },
        "required": ["query"]
    })
    .output_schema({
        "type": "object",
        "properties": {
            "rows": {"type": "array"},
            "row_count": {"type": "integer"},
            "execution_time": {"type": "number"}
        }
    })
    .build()
)
```

### File Operations

```python
file_writer = (
    ToolBuilder("file-writer")
    .description("Writes content to files")
    .input_schema({
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"},
            "encoding": {"type": "string", "default": "utf-8"},
            "append": {"type": "boolean", "default": False}
        },
        "required": ["path", "content"]
    })
    .output_schema({
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "bytes_written": {"type": "integer"},
            "file_path": {"type": "string"}
        }
    })
    .build()
)
```

### Email Sender

```python
email_sender = (
    ToolBuilder("email-sender")
    .description("Sends emails via SMTP")
    .input_schema({
        "type": "object",
        "properties": {
            "to": {"type": "array", "items": {"type": "string", "format": "email"}},
            "subject": {"type": "string"},
            "body": {"type": "string"},
            "attachments": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["to", "subject", "body"]
    })
    .output_schema({
        "type": "object",
        "properties": {
            "sent": {"type": "boolean"},
            "message_id": {"type": "string"},
            "recipients": {"type": "array"}
        }
    })
    .build()
)
```

### API Client

```python
api_client = (
    ToolBuilder("rest-api-client")
    .description("Makes REST API calls")
    .input_schema({
        "type": "object",
        "properties": {
            "endpoint": {"type": "string", "format": "uri"},
            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
            "headers": {"type": "object"},
            "body": {"type": "object"}
        },
        "required": ["endpoint", "method"]
    })
    .output_schema({
        "type": "object",
        "properties": {
            "status_code": {"type": "integer"},
            "headers": {"type": "object"},
            "body": {"type": "object"}
        }
    })
    .build()
)
```

## Tool Naming

**Valid names:**
```python
"web-search"          # ✅ Lowercase with hyphens
"file-writer"         # ✅ Descriptive
"api-client-v2"       # ✅ With version
```

**Invalid names:**
```python
"WebSearch"           # ❌ Must be lowercase
"file_writer"         # ❌ No underscores
"my tool"             # ❌ No spaces
```

## Best Practices

**1. Use descriptive schemas**

```python
# ✅ Clear input contract
input_schema = {
    "type": "object",
    "properties": {
        "search_query": {"type": "string"},
        "result_limit": {"type": "integer", "minimum": 1, "maximum": 100}
    },
    "required": ["search_query"]
}

# ❌ Unclear
input_schema = {
    "type": "object",
    "properties": {
        "q": {"type": "string"},  # What is 'q'?
        "n": {"type": "integer"}   # What is 'n'?
    }
}
```

**2. Provide defaults for optional parameters**

```python
# ✅ Sensible defaults
{
    "properties": {
        "timeout": {"type": "integer", "default": 30},
        "retry_count": {"type": "integer", "default": 3},
        "encoding": {"type": "string", "default": "utf-8"}
    }
}
```

**3. Use appropriate constraints**

```python
# ✅ With validation constraints
{
    "properties": {
        "page_size": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 20
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "url": {
            "type": "string",
            "format": "uri"
        }
    }
}
```

**4. Document expected behavior**

```python
# ✅ Clear description
ToolBuilder("cache-manager")
    .description("Manages in-memory cache with TTL support")

# ❌ Vague
ToolBuilder("manager")
    .description("Does stuff")
```

## Tool vs Module vs Prompt

**Use Tool when:**
- You need external services (APIs, databases, web search)
- Platform provides the integration
- Task involves I/O operations

**Use Module when:**
- You need custom business logic
- Task is computation or data processing
- See [Modules Guide](modules.md)

**Use Prompt when:**
- You need LLM-based reasoning
- Task involves text understanding/generation
- See [Prompts Guide](prompts.md)

## Complete Example

```python
from ainalyn import (
    AgentBuilder,
    WorkflowBuilder,
    NodeBuilder,
    ToolBuilder,
    NodeType
)

# Define tool
search_tool = (
    ToolBuilder("web-search")
    .description("Searches the web for information")
    .input_schema({
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer", "default": 10}
        },
        "required": ["query"]
    })
    .output_schema({
        "type": "object",
        "properties": {
            "results": {"type": "array"},
            "total_found": {"type": "integer"}
        }
    })
    .build()
)

# Use in workflow
workflow = (
    WorkflowBuilder("research")
    .entry_node("search")
    .add_node(
        NodeBuilder("search")
        .description("Search for research topic")
        .node_type(NodeType.TOOL)
        .reference("web-search")
        .inputs(["query"])
        .outputs(["results"])
        .build()
    )
    .build()
)

# Create agent
agent = (
    AgentBuilder("research-agent")
    .version("1.0.0")
    .description("Web research assistant")
    .add_tool(search_tool)
    .add_workflow(workflow)
    .build()
)
```

## See Also

- [ToolBuilder API](../api-reference/builders.md#toolbuilder) - Full API reference
- [Modules Guide](modules.md) - Custom business logic
- [Prompts Guide](prompts.md) - LLM templates
- [Workflows](workflows.md) - Using tools in workflows
