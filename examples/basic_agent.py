"""Basic Agent Example - Simple greeting agent.

This example demonstrates the minimal structure of a functional agent
with a single workflow containing one node.

IMPORTANT:
- This code only DESCRIBES what the agent should do
- The SDK does NOT execute this agent
- All execution happens on Platform Core
"""

from __future__ import annotations

from ainalyn import AgentBuilder, ModuleBuilder, NodeBuilder, WorkflowBuilder
from ainalyn.api import export_yaml, validate


def create_greeting_agent():
    """Create a simple greeting agent."""
    # Define a module for greeting generation
    greeting_module = (
        ModuleBuilder("greeting-generator")
        .description(
            "Generates a personalized greeting message for the user. "
            "Implementation provided by platform EIP."
        )
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "user_name": {"type": "string", "description": "Name of the user"},
                },
                "required": ["user_name"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "greeting": {"type": "string", "description": "Generated greeting"},
                },
            }
        )
        .build()
    )

    # Create a single node
    greet_node = (
        NodeBuilder("generate-greeting")
        .description(
            "Generates a personalized greeting based on the user's name and preferences."
        )
        .uses_module("greeting-generator")
        .inputs("user_name")
        .outputs("greeting")
        .build()
    )

    # Create a workflow with the node
    greet_workflow = (
        WorkflowBuilder("greet-user")
        .description("Simple greeting workflow that generates a personalized message")
        .add_node(greet_node)
        .entry_node("generate-greeting")
        .build()
    )

    # Create the complete agent
    agent = (
        AgentBuilder("greeting-agent")
        .description("A friendly agent that generates personalized greetings")
        .version("1.0.0")
        .add_module(greeting_module)
        .add_workflow(greet_workflow)
        .build()
    )

    return agent


def main():
    """Main execution."""
    print("=" * 60)
    print("Basic Agent Example: Greeting Agent")
    print("=" * 60)

    # Create the agent
    agent = create_greeting_agent()
    print(f"\nCreated agent: {agent.name} v{agent.version}")
    print(f"  Description: {agent.description}")
    print(f"  Workflows: {len(agent.workflows)}")

    # Validate the agent
    print("\nValidating agent definition...")
    result = validate(agent)
    if result.is_valid:
        print("Validation successful!")
    else:
        print("Validation failed:")
        for error in result.errors:
            print(f"  - {error.code}: {error.message}")
        return 1

    # Export to YAML
    print("\nExporting to YAML...")
    yaml_output = export_yaml(agent)

    # Save to file
    output_file = "greeting_agent.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(yaml_output)

    print(f"Exported to {output_file}")

    # Display YAML
    print("\n" + "=" * 60)
    print("Generated YAML:")
    print("=" * 60)
    print(yaml_output)

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
