"""Basic Agent Example - Simple greeting agent.

This example demonstrates the minimal structure of a functional agent
with a single workflow containing one node.
"""
from __future__ import annotations

from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate, export_yaml


def create_greeting_agent():
    """Create a simple greeting agent."""
    # Create a single node
    greet_node = (
        NodeBuilder("generate_greeting")
        .goal("Generate a personalized greeting message for the user")
        .description(
            "This node creates a friendly, personalized greeting based on "
            "the user's name and preferences."
        )
        .build()
    )

    # Create a workflow with the node
    greet_workflow = (
        WorkflowBuilder("greet_user")
        .description("Simple greeting workflow")
        .add_node(greet_node)
        .build()
    )

    # Create the complete agent
    agent = (
        AgentBuilder("GreetingAgent")
        .description("A friendly agent that generates personalized greetings")
        .version("1.0.0")
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
    print(f"\n✅ Created agent: {agent.name} v{agent.version}")
    print(f"   Description: {agent.description}")
    print(f"   Workflows: {len(agent.workflows)}")

    # Validate the agent
    print("\n🔍 Validating agent definition...")
    try:
        validate(agent)
        print("✅ Validation successful!")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1

    # Export to YAML
    print("\n📦 Exporting to YAML...")
    yaml_output = export_yaml(agent)

    # Save to file
    output_file = "greeting_agent.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(yaml_output)

    print(f"✅ Exported to {output_file}")

    # Display YAML
    print("\n" + "=" * 60)
    print("Generated YAML:")
    print("=" * 60)
    print(yaml_output)

    print("\n" + "=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
