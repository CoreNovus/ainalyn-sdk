"""Multi-Workflow Agent Example - Data analysis agent with multiple workflows.

This example demonstrates an agent with multiple workflows, showing how to
organize complex functionality into separate workflows for different use cases.
"""
from __future__ import annotations

from ainalyn import AgentBuilder, WorkflowBuilder, NodeBuilder
from ainalyn.api import validate, export_yaml


def create_data_analyst_agent():
    """Create a data analysis agent with multiple workflows."""
    # ============================================================
    # Workflow 1: Full Analysis
    # ============================================================
    full_analysis_workflow = (
        WorkflowBuilder("full_analysis")
        .description("Complete data analysis pipeline with detailed reporting")
        .add_node(
            NodeBuilder("load_data")
            .goal("Load data from specified source")
            .description("Supports CSV, JSON, and database sources")
            .build()
        )
        .add_node(
            NodeBuilder("clean_data")
            .goal("Clean and preprocess the loaded data")
            .description("Handles missing values, outliers, and type conversions")
            .depends_on("load_data")
            .build()
        )
        .add_node(
            NodeBuilder("analyze_data")
            .goal("Perform statistical analysis on cleaned data")
            .description("Calculates summary statistics, correlations, and distributions")
            .depends_on("clean_data")
            .build()
        )
        .add_node(
            NodeBuilder("visualize_data")
            .goal("Create visualizations of the analysis results")
            .description("Generates charts, graphs, and plots")
            .depends_on("analyze_data")
            .build()
        )
        .add_node(
            NodeBuilder("generate_report")
            .goal("Compile a comprehensive analysis report")
            .description("Creates a formatted report with findings and visualizations")
            .depends_on("analyze_data", "visualize_data")
            .build()
        )
        .build()
    )

    # ============================================================
    # Workflow 2: Quick Summary
    # ============================================================
    quick_summary_workflow = (
        WorkflowBuilder("quick_summary")
        .description("Fast summary statistics without detailed analysis")
        .add_node(
            NodeBuilder("load_data")
            .goal("Load data from specified source")
            .build()
        )
        .add_node(
            NodeBuilder("calculate_summary")
            .goal("Calculate basic summary statistics")
            .description("Mean, median, mode, standard deviation, etc.")
            .depends_on("load_data")
            .build()
        )
        .build()
    )

    # ============================================================
    # Workflow 3: Data Validation
    # ============================================================
    validation_workflow = (
        WorkflowBuilder("validate_data")
        .description("Validate data quality and schema compliance")
        .add_node(
            NodeBuilder("load_data")
            .goal("Load data from specified source")
            .build()
        )
        .add_node(
            NodeBuilder("check_schema")
            .goal("Validate data schema and structure")
            .description("Ensures columns, types, and constraints are correct")
            .depends_on("load_data")
            .build()
        )
        .add_node(
            NodeBuilder("check_quality")
            .goal("Assess data quality metrics")
            .description("Checks completeness, accuracy, and consistency")
            .depends_on("load_data")
            .build()
        )
        .add_node(
            NodeBuilder("generate_validation_report")
            .goal("Create validation report with findings")
            .depends_on("check_schema", "check_quality")
            .build()
        )
        .build()
    )

    # ============================================================
    # Create Agent with All Workflows
    # ============================================================
    agent = (
        AgentBuilder("DataAnalyst")
        .description(
            "Comprehensive data analysis agent supporting full analysis, "
            "quick summaries, and data validation workflows"
        )
        .version("2.0.0")
        .add_workflow(full_analysis_workflow)
        .add_workflow(quick_summary_workflow)
        .add_workflow(validation_workflow)
        .build()
    )

    return agent


def main():
    """Main execution."""
    print("=" * 70)
    print("Multi-Workflow Agent Example: Data Analyst")
    print("=" * 70)

    # Create the agent
    agent = create_data_analyst_agent()
    print(f"\n✅ Created agent: {agent.name} v{agent.version}")
    print(f"   Description: {agent.description}")
    print(f"   Workflows: {len(agent.workflows)}")

    # Display workflow details
    print("\n📋 Workflow Details:")
    for i, workflow in enumerate(agent.workflows, 1):
        print(f"\n   {i}. {workflow.name}")
        print(f"      Description: {workflow.description}")
        print(f"      Nodes: {len(workflow.nodes)}")
        for node in workflow.nodes:
            deps = f" (depends on: {', '.join(node.dependencies)})" if node.dependencies else ""
            print(f"        - {node.name}{deps}")

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
    output_file = "data_analyst_agent.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(yaml_output)

    print(f"✅ Exported to {output_file}")

    # Display YAML (truncated for readability)
    print("\n" + "=" * 70)
    print("Generated YAML (preview):")
    print("=" * 70)
    lines = yaml_output.split("\n")
    preview_lines = min(30, len(lines))
    print("\n".join(lines[:preview_lines]))
    if len(lines) > preview_lines:
        print(f"\n... ({len(lines) - preview_lines} more lines)")

    print("\n" + "=" * 70)
    print("✅ Example completed successfully!")
    print("=" * 70)
    print("\n💡 Key Takeaways:")
    print("   - Agents can have multiple workflows for different use cases")
    print("   - Each workflow can have a different number of nodes")
    print("   - Nodes can have dependencies within their workflow")
    print(f"   - This agent has {sum(len(w.nodes) for w in agent.workflows)} total nodes across {len(agent.workflows)} workflows")

    return 0


if __name__ == "__main__":
    exit(main())
