# Platform Boundaries

Understanding the **boundaries** between the Ainalyn SDK and the Ainalyn Platform is **critical** for successful agent development. This document defines what the SDK can and cannot do.

!!! danger "Most Important Concept"
    **The SDK is a compiler, NOT a runtime.** Everything you build with the SDK is a **description** of an agent, not an executing system. Execution authority belongs solely to the Ainalyn Platform.

## The Four Core Concepts

The Ainalyn ecosystem is built on four foundational concepts:

### 1. Agent (Marketplace Contract Entity)

- **What it is**: A task-oriented product entity that can be scheduled, governed, and billed
- **SDK role**: Define the agent's structure and capabilities
- **Platform role**: Host, manage, and enable execution of agents

!!! example "Agent ≠"
    - ❌ Not a workflow
    - ❌ Not a node or module
    - ❌ Not an LLM or autonomous system
    - ❌ Not a runtime process

### 2. Agent Definition (Description Layer Only)

- **What it is**: The specification of an agent's structure, workflows, and capabilities
- **SDK role**: Compile valid agent definitions to YAML
- **Platform role**: Parse and validate definitions for deployment

!!! success "SDK Creates Agent Definitions"
    This is the **entire scope** of the SDK: creating valid `AgentDefinition` objects and exporting them to YAML.

### 3. Execution (Platform Core Only)

- **What it is**: The runtime instance of an agent performing a task
- **SDK role**: **NONE** - The SDK cannot execute anything
- **Platform role**: Create, manage, and complete executions

!!! warning "Critical Distinction"
    - `AgentDefinition` (SDK) ≠ `Execution` (Platform)
    - You define agents, the platform executes them
    - SDK has **ZERO authority** over execution

### 4. Billing (Execution-Based Only)

- **What it is**: Charges based on completed executions
- **SDK role**: **NONE** - The SDK cannot calculate billing
- **Platform role**: Track execution costs and bill users

## What the SDK CAN Do

The SDK is **authorized** to:

### ✅ Define Agent Structures

```python
from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder

agent = (
    AgentBuilder("MyAgent")
    .description("What the agent does")
    .version("1.0.0")
    .add_workflow(...)
    .build()
)
```

### ✅ Validate Definitions

```python
from ainalyn.api import validate

validate(agent)  # Ensures compliance with platform rules
```

### ✅ Export to YAML

```python
from ainalyn.api import export_yaml

yaml_output = export_yaml(agent)  # Platform-compatible format
```

### ✅ Provide Local Development Tools

```python
# Testing utilities (for development only)
from ainalyn.adapters.secondary import StaticAnalyzer

analyzer = StaticAnalyzer()
issues = analyzer.analyze(agent)  # Find potential problems
```

### ✅ Offer Type-Safe APIs

```python
# Full type hints for IDE support
from ainalyn import AgentBuilder

builder: AgentBuilder = AgentBuilder("MyAgent")  # Type-safe!
```

## What the SDK CANNOT Do (Forbidden Zone)

The SDK is **explicitly forbidden** from:

### ❌ Execution Semantics

**NO execution methods:**

```python
# ❌ FORBIDDEN - These methods do NOT exist
agent.execute()
agent.run()
agent.start()
workflow.execute()
node.run()
```

**Why?** Execution is the platform's exclusive responsibility. The SDK only describes what should be executed, not how or when.

### ❌ Execution Authority

**NO decisions about:**

- Retry strategies
- Timeout policies
- Fallback mechanisms
- Success/failure determination
- Execution scheduling
- Resource allocation

**Why?** The platform must have sole authority over these operational decisions to ensure consistency, reliability, and governance.

### ❌ Billing and Pricing Logic

**NO billing calculations:**

```python
# ❌ FORBIDDEN - Cannot exist in SDK
agent.calculate_cost()
execution.get_price()
agent.set_pricing(...)
```

**Why?** Billing is based on platform-managed executions, not agent definitions. The SDK cannot know execution costs.

### ❌ Autonomous Agent Patterns

**NO autonomous behaviors:**

- Self-triggered executions
- Continuous running loops
- Independent decision-making
- State persistence across executions

**Why?** Agents on the Ainalyn Platform are **task-oriented**, not autonomous. They execute specific tasks on demand, then complete.

### ❌ Execution ID Generation

**NO execution tracking:**

```python
# ❌ FORBIDDEN
agent.create_execution_id()
agent.track_execution(...)
```

**Why?** Only the platform can create and manage `executionId`s, which are used for billing, tracking, and governance.

### ❌ Platform Authority

**NO platform-level operations:**

- Agent marketplace operations
- User authentication/authorization
- Platform configuration
- Infrastructure management

**Why?** These are platform responsibilities, far beyond the SDK's scope as a compiler.

## The SDK/Platform Contract

### SDK Responsibilities

1. **Define**: Provide APIs for defining agents
2. **Validate**: Ensure definitions comply with rules
3. **Compile**: Export to platform-compatible YAML
4. **Document**: Help developers understand boundaries

### Platform Responsibilities

1. **Execute**: Run agent definitions as executions
2. **Bill**: Charge for execution completion
3. **Govern**: Enforce policies and limits
4. **Host**: Provide infrastructure and marketplace

### Clear Separation

```
┌─────────────────────────────────────────────────────────┐
│                    DEVELOPER                            │
│                        │                                │
│                        ▼                                │
│              ┌──────────────────┐                       │
│              │  Ainalyn SDK     │                       │
│              │  (Compiler)      │                       │
│              └────────┬─────────┘                       │
│                       │                                 │
│                       │ YAML                            │
│                       ▼                                 │
│              ┌──────────────────┐                       │
│              │ Ainalyn Platform │                       │
│              │  (Runtime)       │                       │
│              └────────┬─────────┘                       │
│                       │                                 │
│                       ▼                                 │
│              ┌──────────────────┐                       │
│              │   Execution      │                       │
│              │  (Runtime        │                       │
│              │   Instance)      │                       │
│              └──────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

## Local Testing vs Platform Execution

!!! warning "Critical Distinction"
    **Local run ≠ Platform execution**

### Local Testing (SDK Development Mode)

```python
# For development ONLY
# NOT representative of platform execution!

# You might create test utilities
def test_agent_structure(agent):
    """Test that agent definition is well-formed."""
    assert agent.name
    assert len(agent.workflows) > 0
    # etc.
```

**Purpose**: Validate structure, not behavior

### Platform Execution (Production)

- Agent definition is deployed to platform
- Platform parses YAML
- Platform creates `Execution` instances
- Platform manages execution lifecycle
- Platform bills based on execution results

**Purpose**: Actual task completion

## Execution Lifecycle (Platform Only)

The platform manages this lifecycle (SDK has **no role**):

```
REQUESTED → VALIDATED → SCHEDULED → RUNNING → COMPLETED/FAILED/ABORTED
```

1. **REQUESTED**: User requests task execution
2. **VALIDATED**: Platform validates request
3. **SCHEDULED**: Platform schedules execution
4. **RUNNING**: Platform executes agent logic
5. **COMPLETED/FAILED/ABORTED**: Platform finalizes execution

**SDK involvement**: NONE. The SDK's work ends at agent definition compilation.

## EIP (Execution Implementation Provider)

EIPs provide execution capabilities but **NOT execution authority**:

- **EIP provides**: LLM APIs, tool integrations, compute resources
- **Platform decides**: When to use EIP, retry logic, timeout handling
- **SDK role**: NONE - EIP is a platform concept

## Boundary Compliance Checklist

When developing with the SDK, ensure:

- ✅ No execution-related methods (`execute()`, `run()`, `start()`)
- ✅ No state management across executions
- ✅ No billing/pricing calculations
- ✅ No `executionId` generation or tracking
- ✅ No platform authority operations
- ✅ All agent definitions include disclaimer comments
- ✅ Documentation emphasizes "compiler, not runtime"

## Disclaimer Requirements

All agent definitions should include a disclaimer:

```python
"""
MyAgent - A task-oriented agent.

IMPORTANT: This is an agent DEFINITION, not a runtime implementation.
Execution authority belongs to the Ainalyn Platform.
"""
```

## Why These Boundaries Matter

### 1. Clear Responsibility

- SDK: Definition quality
- Platform: Execution reliability
- No confusion about who handles what

### 2. Platform Governance

- Platform can enforce policies consistently
- Platform can evolve execution strategies
- Platform can ensure billing accuracy

### 3. Developer Focus

- Developers focus on agent logic
- Developers don't manage infrastructure
- Developers don't implement execution engines

### 4. Security and Trust

- Platform controls resource access
- Platform prevents malicious execution
- Platform ensures fair billing

## Common Misconceptions

### ❌ "The SDK runs my agent locally"

**Wrong.** The SDK defines your agent. Local testing (if provided) is structural validation only, not actual execution.

### ❌ "I can optimize execution with SDK settings"

**Wrong.** Execution optimization is the platform's job. Your agent definition describes WHAT, not HOW.

### ❌ "My agent will retry automatically"

**Wrong.** Retry logic is a platform decision, not defined in your agent. The platform determines retry strategies.

### ❌ "I can estimate costs in the SDK"

**Wrong.** Costs depend on platform execution, which varies based on actual runtime behavior, not static definitions.

## Further Reading

- **[Compiler vs Runtime](compiler-not-runtime.md)** - Deep dive into the paradigm
- **[Agent Definition](agent-definition.md)** - What you're actually building
- **[Architecture Overview](architecture-overview.md)** - How the SDK is designed
- **[Boundary Compliance](../contributor-guide/boundary-compliance.md)** - For SDK contributors

## Reference Specifications

These concepts are derived from the official boundary specifications:

- `ref-boundary/Platform Vision & System Boundary.md`
- `ref-boundary/Agent Definition Compiler & Runtime Forbidden Zone.md`
- `ref-boundary/Agent Canonical Definition.md`
- `ref-boundary/Execution Lifecycle & Authority.md`
- `ref-boundary/Execution Billing, Pricing & Revenue Boundary.md`

---

**Remember**: The SDK is a powerful compiler for agent definitions. Stay within the boundaries, and you'll build amazing agents for the Ainalyn Platform! 🚀
