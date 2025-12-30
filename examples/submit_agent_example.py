"""
Example: Submitting an Agent to Platform Core.

This example demonstrates how to:
1. Build an agent definition
2. Validate it locally
3. Submit it to Platform Core for review
4. Track the submission status

Important - Platform Constitution:
- SDK can submit but NOT approve (Platform Core has final authority)
- Submission does NOT create an Execution
- Submission does NOT incur billing (unless platform policy states)
- Platform Core may apply additional validation beyond SDK validation

Note:
    Currently uses MockPlatformClient for testing until Platform Core
    API is available. All submissions are simulated.
"""

from __future__ import annotations

import os
import time

from ainalyn import (
    AgentBuilder,
    AuthenticationError,
    FeedbackSeverity,
    NetworkError,
    NodeBuilder,
    PromptBuilder,
    SubmissionError,
    SubmissionStatus,
    ToolBuilder,
    WorkflowBuilder,
    submit_agent,
    track_submission,
    validate,
)


def main() -> None:
    """Demonstrate agent submission workflow."""
    print("=" * 70)
    print("Ainalyn SDK - Agent Submission Example")
    print("=" * 70)
    print()

    # Step 1: Build an agent definition
    print("Step 1: Building agent definition...")
    print("-" * 70)

    # Define a tool for fetching weather data
    weather_tool = (
        ToolBuilder("weather-api")
        .description("Fetch current weather data for a location")
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates",
                    }
                },
                "required": ["location"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number"},
                    "conditions": {"type": "string"},
                },
            }
        )
        .build()
    )

    # Define a prompt for formatting weather responses
    weather_prompt = (
        PromptBuilder("weather-response")
        .content(
            "Format the following weather data in a user-friendly way:\n"
            "Location: {{location}}\n"
            "Temperature: {{temperature}}°C\n"
            "Conditions: {{conditions}}"
        )
        .build()
    )

    # Define workflow nodes
    fetch_node = NodeBuilder("fetch", "module").reference("weather-fetcher").build()

    format_node = NodeBuilder("format", "prompt").reference("weather-response").build()

    # Define a workflow
    weather_workflow = (
        WorkflowBuilder("main")
        .description("Fetch and format weather data")
        .add_node(fetch_node)
        .add_node(format_node)
        .add_edge("fetch", "format")
        .entry_node("fetch")
        .build()
    )

    # Build the complete agent
    agent = (
        AgentBuilder("weather-assistant")
        .version("1.0.0")
        .description("A helpful assistant that provides weather information")
        .add_workflow(weather_workflow)
        .add_tool(weather_tool)
        .add_prompt(weather_prompt)
        .build()
    )

    print(f"✓ Built agent: {agent.name} v{agent.version}")
    print(f"  Description: {agent.description}")
    print(f"  Workflows: {len(agent.workflows)}")
    print(f"  Tools: {len(agent.tools)}")
    print(f"  Prompts: {len(agent.prompts)}")
    print()

    # Step 2: Validate locally (recommended before submission)
    print("Step 2: Validating agent locally...")
    print("-" * 70)

    validation_result = validate(agent)

    if validation_result.is_valid:
        print("✓ Validation passed!")
        print()
    else:
        print("✗ Validation failed:")
        for error in validation_result.errors:
            print(f"  [{error.severity.value}] {error.code}: {error.message}")
        print()
        print("Cannot submit invalid agent. Please fix errors and try again.")
        return

    # Step 3: Submit to Platform Core
    print("Step 3: Submitting agent to Platform Core...")
    print("-" * 70)

    # Get API key from environment variable (recommended)
    # For demo purposes, we use a mock key
    api_key = os.getenv("AINALYN_API_KEY", "dev_mock_demo_key")

    if api_key == "dev_mock_demo_key":
        print("⚠ Using mock API key for demonstration")
        print("  In production, set AINALYN_API_KEY environment variable")
        print("  Get your API key at: https://console.ainalyn.io/api-keys")
        print()

    try:
        # Submit the agent
        result = submit_agent(
            definition=agent,
            api_key=api_key,
            auto_deploy=False,  # Manual review before deployment
        )

        print(f"✓ Submission successful!")
        print(f"  Review ID: {result.review_id}")
        print(f"  Status: {result.status.value}")
        print(f"  Submitted at: {result.submitted_at}")
        print(f"  Track at: {result.tracking_url}")

        if result.estimated_review_time:
            print(f"  Estimated review time: {result.estimated_review_time}")

        # Display any immediate feedback
        if result.feedback:
            print()
            print("  Platform Feedback:")
            for feedback in result.feedback:
                severity_symbol = {
                    FeedbackSeverity.ERROR: "✗",
                    FeedbackSeverity.WARNING: "⚠",
                    FeedbackSeverity.INFO: "ℹ",
                }[feedback.severity]
                print(
                    f"    {severity_symbol} [{feedback.category.value}] {feedback.message}"
                )

        print()

        # Step 4: Track submission status
        print("Step 4: Tracking submission status...")
        print("-" * 70)

        # In a real scenario, you might poll this periodically
        # For demo, we simulate checking status
        print("Checking submission status...")
        time.sleep(1)  # Simulate waiting

        status_result = track_submission(
            review_id=result.review_id,
            api_key=api_key,
        )

        print(f"  Current status: {status_result.status.value}")

        if status_result.is_live:
            print(f"  🎉 Agent is LIVE!")
            print(f"  Agent ID: {status_result.agent_id}")
            print(f"  Marketplace: {status_result.marketplace_url}")

        elif status_result.status == SubmissionStatus.PENDING_REVIEW:
            print(f"  ⏳ Review in progress...")
            print(f"  Track at: {status_result.tracking_url}")

        elif status_result.is_rejected:
            print(f"  ✗ Submission REJECTED")
            print()
            print("  Blocking Issues:")
            for issue in status_result.get_blocking_issues():
                print(f"    - {issue.message}")
                if issue.path:
                    print(f"      Location: {issue.path}")
            print()
            print("  Fix these issues and resubmit.")

        # Display all feedback
        if status_result.feedback:
            print()
            print("  All Feedback:")
            for feedback in status_result.feedback:
                print(f"    [{feedback.severity.value}] {feedback.message}")

        print()

    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e.message}")
        print("  Check your API key at: https://console.ainalyn.io/api-keys")
        print()

    except NetworkError as e:
        print(f"✗ Network error: {e.message}")
        print("  Check your internet connection and try again.")
        print()

    except SubmissionError as e:
        print(f"✗ Submission failed: {e.message}")

        if e.validation_errors:
            print()
            print("  Validation Errors:")
            for error in e.validation_errors:
                print(f"    [{error.severity.value}] {error.code}: {error.message}")
        print()

    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print()
    print("This example demonstrated:")
    print("  1. Building an agent definition")
    print("  2. Validating locally (recommended)")
    print("  3. Submitting to Platform Core")
    print("  4. Tracking submission status")
    print()
    print("Important Reminders:")
    print("  - SDK can submit but NOT approve")
    print("  - Platform Core has final authority")
    print("  - Submission does NOT create an Execution")
    print("  - Currently using MockPlatformClient (for testing)")
    print()
    print("Next Steps:")
    print("  - Get your API key: https://console.ainalyn.io/api-keys")
    print("  - Read submission guide: https://docs.ainalyn.io/sdk/submission")
    print("  - Explore platform policies: https://docs.ainalyn.io/platform/policies")
    print()


if __name__ == "__main__":
    main()
