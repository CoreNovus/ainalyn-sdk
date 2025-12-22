"""Price Monitoring and Notification Agent Example.

This example demonstrates the complete SDK workflow as defined in ISSUE#1-sdk:
1. Developer writes authoring-time code using the SDK
2. SDK compiles this code into a non-executable definition artifact
3. The artifact is submitted to the platform for execution

IMPORTANT:
- This code only DESCRIBES what the agent should do
- The SDK does NOT execute this agent
- All execution happens on Platform Core
- Local compilation does NOT equal platform execution

Scenario:
A price monitoring agent that:
- Accepts user input (route, threshold, notification target)
- Fetches price data using a platform-provided tool
- Applies a condition check
- Sends notification if threshold is exceeded
"""

from __future__ import annotations

from pathlib import Path

from ainalyn import (
    AgentBuilder,
    ModuleBuilder,
    NodeBuilder,
    PromptBuilder,
    ToolBuilder,
    WorkflowBuilder,
)
from ainalyn.api import compile_agent, validate


def create_price_monitor_agent():
    """
    Create a Price Monitoring and Notification Agent.

    This function demonstrates SDK authoring code - it DESCRIBES
    an agent definition, it does NOT create executable code.

    The agent workflow:
    1. fetch-price: Fetches current price data
    2. check-threshold: Evaluates if price exceeds threshold
    3. send-notification: Sends alert if condition is met

    Returns:
        AgentDefinition: A compiled agent definition artifact.
    """
    # ================================================================
    # Step 1: Define Modules (reusable capability descriptions)
    # ================================================================

    # Module: Price data fetcher
    # NOTE: This only DESCRIBES the interface, not the implementation
    price_fetcher = (
        ModuleBuilder("price-fetcher")
        .description(
            "Fetches current price data for a specified route. "
            "Implementation provided by platform EIP."
        )
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin location code"},
                    "destination": {
                        "type": "string",
                        "description": "Destination location code",
                    },
                    "date": {
                        "type": "string",
                        "format": "date",
                        "description": "Travel date",
                    },
                },
                "required": ["origin", "destination", "date"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "current_price": {
                        "type": "number",
                        "description": "Current price in user currency",
                    },
                    "currency": {"type": "string"},
                    "provider": {"type": "string"},
                    "fetched_at": {"type": "string", "format": "date-time"},
                },
            }
        )
        .build()
    )

    # Module: Threshold checker
    threshold_checker = (
        ModuleBuilder("threshold-checker")
        .description(
            "Compares current price against user-defined threshold. "
            "Returns whether notification should be triggered."
        )
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "current_price": {"type": "number"},
                    "threshold": {"type": "number"},
                    "comparison": {
                        "type": "string",
                        "enum": ["below", "above"],
                        "description": "Trigger when price is below/above threshold",
                    },
                },
                "required": ["current_price", "threshold", "comparison"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "should_notify": {"type": "boolean"},
                    "price_difference": {"type": "number"},
                    "message": {"type": "string"},
                },
            }
        )
        .build()
    )

    # ================================================================
    # Step 2: Define Tools (external capability interfaces)
    # ================================================================

    # Tool: Notification sender
    # NOTE: This DECLARES the tool interface, actual sending is done by platform
    notification_tool = (
        ToolBuilder("notification-sender")
        .description(
            "Sends notification to user via their preferred channel. "
            "Actual delivery handled by platform notification service."
        )
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "User ID or contact identifier",
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["email", "sms", "push"],
                        "description": "Notification delivery channel",
                    },
                    "title": {"type": "string"},
                    "message": {"type": "string"},
                },
                "required": ["recipient", "channel", "message"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "sent": {"type": "boolean"},
                    "notification_id": {"type": "string"},
                },
            }
        )
        .build()
    )

    # ================================================================
    # Step 3: Define Prompt (LLM prompt template)
    # ================================================================

    # Prompt: Format notification message
    format_message_prompt = (
        PromptBuilder("format-notification")
        .description("Formats a user-friendly notification message about price alert")
        .template(
            """You are a helpful assistant that formats price alert notifications.

Given the following price information:
- Route: {{origin}} to {{destination}}
- Current Price: {{current_price}} {{currency}}
- User Threshold: {{threshold}} {{currency}}
- Price Difference: {{price_difference}} {{currency}}

Write a brief, friendly notification message (2-3 sentences) informing the user
that the price has dropped below their threshold and they may want to book soon.
"""
        )
        .variables(
            "origin",
            "destination",
            "current_price",
            "currency",
            "threshold",
            "price_difference",
        )
        .build()
    )

    # ================================================================
    # Step 4: Define Workflow (task flow description)
    # ================================================================

    # Build nodes for the workflow
    fetch_node = (
        NodeBuilder("fetch-price")
        .description("Fetches current price data for the user-specified route")
        .uses_module("price-fetcher")
        .inputs("origin", "destination", "date")
        .outputs("current_price", "currency", "provider")
        .next_nodes("check-threshold")
        .build()
    )

    check_node = (
        NodeBuilder("check-threshold")
        .description("Checks if the fetched price meets the user threshold condition")
        .uses_module("threshold-checker")
        .inputs("current_price", "threshold", "comparison")
        .outputs("should_notify", "price_difference", "message")
        .next_nodes("format-message")
        .build()
    )

    format_node = (
        NodeBuilder("format-message")
        .description("Formats a user-friendly notification message using LLM")
        .uses_prompt("format-notification")
        .inputs(
            "origin",
            "destination",
            "current_price",
            "currency",
            "threshold",
            "price_difference",
        )
        .outputs("formatted_message")
        .next_nodes("send-notification")
        .build()
    )

    notify_node = (
        NodeBuilder("send-notification")
        .description("Sends the formatted notification to the user")
        .uses_tool("notification-sender")
        .inputs("recipient", "channel", "formatted_message")
        .outputs("sent", "notification_id")
        .build()
    )

    # Build the workflow
    monitor_workflow = (
        WorkflowBuilder("price-monitor")
        .description(
            "Monitors price for a route and notifies user when threshold is met. "
            "This workflow describes the task flow - actual execution is by Platform Core."
        )
        .add_node(fetch_node)
        .add_node(check_node)
        .add_node(format_node)
        .add_node(notify_node)
        .entry_node("fetch-price")
        .build()
    )

    # ================================================================
    # Step 5: Build the Agent Definition
    # ================================================================

    agent = (
        AgentBuilder("price-monitor-agent")
        .version("1.0.0")
        .description(
            "Monitors travel prices and sends notifications when prices drop "
            "below user-defined thresholds. This is a task-oriented agent that "
            "completes a specific goal - it is NOT an autonomous system."
        )
        .add_module(price_fetcher)
        .add_module(threshold_checker)
        .add_tool(notification_tool)
        .add_prompt(format_message_prompt)
        .add_workflow(monitor_workflow)
        .build()
    )

    return agent


def main():
    """
    Main function demonstrating the complete SDK workflow.

    This demonstrates:
    1. Authoring code (create_price_monitor_agent)
    2. Validation (validate)
    3. Compilation to artifact (compile_agent)

    The output YAML is what gets submitted to the Developer Console.
    """
    print("=" * 70)
    print("Price Monitoring Agent - SDK Authoring Example")
    print("=" * 70)
    print()
    print("This example demonstrates the correct SDK development model:")
    print("  1. Write authoring-time code using the SDK")
    print("  2. Compile to a non-executable definition artifact")
    print("  3. Submit artifact to platform for execution")
    print()
    print("IMPORTANT: The SDK is a COMPILER, not a RUNTIME.")
    print("           Local compilation does NOT equal platform execution.")
    print()
    print("-" * 70)

    # Step 1: Create the agent definition
    print("\n[Step 1] Creating agent definition...")
    agent = create_price_monitor_agent()
    print(f"  Agent: {agent.name} v{agent.version}")
    print(f"  Description: {agent.description[:60]}...")
    print(f"  Modules: {len(agent.modules)}")
    print(f"  Tools: {len(agent.tools)}")
    print(f"  Prompts: {len(agent.prompts)}")
    print(f"  Workflows: {len(agent.workflows)}")

    # Step 2: Validate the definition
    print("\n[Step 2] Validating agent definition...")
    result = validate(agent)
    if result.is_valid:
        print("  Validation: PASSED")
        if result.has_warnings:
            print(f"  Warnings: {len([e for e in result.errors if e.severity.value == 'warning'])}")
    else:
        print("  Validation: FAILED")
        for error in result.errors:
            print(f"    - {error.code}: {error.message}")
        return 1

    # Step 3: Compile to YAML artifact
    print("\n[Step 3] Compiling to YAML artifact...")
    output_path = Path("price_monitor_agent.yaml")
    compile_result = compile_agent(agent, output_path)

    if compile_result.is_successful:
        print(f"  Output: {output_path}")
        print(f"  Size: {len(compile_result.yaml_content or '')} bytes")
    else:
        print("  Compilation: FAILED")
        return 1

    # Display the compiled artifact
    print("\n" + "=" * 70)
    print("COMPILED ARTIFACT (Agent Definition YAML)")
    print("=" * 70)
    print()
    print("This YAML file is what you submit to the Developer Console.")
    print("It contains ONLY descriptions - no executable code.")
    print()
    print("-" * 70)
    print(compile_result.yaml_content)
    print("-" * 70)

    # Explain next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS: Submitting to Platform")
    print("=" * 70)
    print("""
After compilation, submit the YAML artifact to the Ainalyn Platform:

1. Upload via Developer Console:
   - Log in to https://console.ainalyn.io
   - Navigate to "My Agents" > "Create New Agent"
   - Upload the generated YAML file
   - Platform validates the definition
   - Once approved, agent becomes available for execution

2. Upload via CLI (when available):
   $ ainalyn deploy price_monitor_agent.yaml

3. Upload via API (when available):
   POST /api/v1/agents
   Content-Type: application/yaml
   Body: <yaml content>

REMEMBER:
- The YAML file is a DESCRIPTION, not executable code
- Platform Core handles all execution
- Billing is based on Platform Execution, not SDK compilation
- You cannot "run" this agent locally - only the platform can execute it
""")

    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
