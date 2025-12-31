"""Multi-Workflow Agent Example - Data analysis agent with multiple workflows.

This example demonstrates an agent with multiple workflows, showing how to
organize complex functionality into separate workflows for different use cases.

IMPORTANT:
- This code only DESCRIBES what the agent should do
- The SDK does NOT execute this agent
- All execution happens on Platform Core
"""

from __future__ import annotations

from ainalyn import AgentBuilder, ModuleBuilder, NodeBuilder, WorkflowBuilder
from ainalyn.api import export_yaml, validate


def create_data_analyst_agent():
    """Create a data analysis agent with multiple workflows."""
    # ================================================================
    # Define Modules
    # ================================================================

    data_loader = (
        ModuleBuilder("data-loader")
        .description("Loads data from specified source (CSV, JSON, database)")
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "source_type": {
                        "type": "string",
                        "enum": ["csv", "json", "database"],
                    },
                    "source_path": {"type": "string"},
                },
                "required": ["source_type", "source_path"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "data": {"type": "array"},
                    "row_count": {"type": "integer"},
                },
            }
        )
        .build()
    )

    data_cleaner = (
        ModuleBuilder("data-cleaner")
        .description("Handles missing values, outliers, and type conversions")
        .input_schema({"type": "object", "properties": {"data": {"type": "array"}}})
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "cleaned_data": {"type": "array"},
                    "removed_count": {"type": "integer"},
                },
            }
        )
        .build()
    )

    stats_calculator = (
        ModuleBuilder("stats-calculator")
        .description("Calculates summary statistics, correlations, and distributions")
        .input_schema({"type": "object", "properties": {"data": {"type": "array"}}})
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "mean": {"type": "number"},
                    "median": {"type": "number"},
                    "std_dev": {"type": "number"},
                    "correlations": {"type": "object"},
                },
            }
        )
        .build()
    )

    visualizer = (
        ModuleBuilder("data-visualizer")
        .description("Generates charts, graphs, and plots from data")
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "data": {"type": "array"},
                    "chart_type": {"type": "string"},
                },
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "chart_url": {"type": "string"},
                },
            }
        )
        .build()
    )

    report_generator = (
        ModuleBuilder("report-generator")
        .description("Creates formatted reports with findings and visualizations")
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "statistics": {"type": "object"},
                    "charts": {"type": "array"},
                },
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "report_url": {"type": "string"},
                },
            }
        )
        .build()
    )

    schema_validator = (
        ModuleBuilder("schema-validator")
        .description("Validates data schema and structure")
        .input_schema({"type": "object", "properties": {"data": {"type": "array"}}})
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "is_valid": {"type": "boolean"},
                    "errors": {"type": "array"},
                },
            }
        )
        .build()
    )

    quality_checker = (
        ModuleBuilder("quality-checker")
        .description(
            "Assesses data quality metrics: completeness, accuracy, consistency"
        )
        .input_schema({"type": "object", "properties": {"data": {"type": "array"}}})
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "completeness_score": {"type": "number"},
                    "accuracy_score": {"type": "number"},
                    "issues": {"type": "array"},
                },
            }
        )
        .build()
    )

    # ================================================================
    # Workflow 1: Full Analysis
    # ================================================================
    full_analysis_workflow = (
        WorkflowBuilder("full-analysis")
        .description("Complete data analysis pipeline with detailed reporting")
        .add_node(
            NodeBuilder("load-data")
            .description("Load data from specified source")
            .uses_module("data-loader")
            .inputs("source_type", "source_path")
            .outputs("data", "row_count")
            .next_nodes("clean-data")
            .build()
        )
        .add_node(
            NodeBuilder("clean-data")
            .description("Clean and preprocess the loaded data")
            .uses_module("data-cleaner")
            .inputs("data")
            .outputs("cleaned_data", "removed_count")
            .next_nodes("analyze-data")
            .build()
        )
        .add_node(
            NodeBuilder("analyze-data")
            .description("Perform statistical analysis on cleaned data")
            .uses_module("stats-calculator")
            .inputs("cleaned_data")
            .outputs("statistics")
            .next_nodes("visualize-data")
            .build()
        )
        .add_node(
            NodeBuilder("visualize-data")
            .description("Create visualizations of the analysis results")
            .uses_module("data-visualizer")
            .inputs("cleaned_data", "statistics")
            .outputs("charts")
            .next_nodes("generate-report")
            .build()
        )
        .add_node(
            NodeBuilder("generate-report")
            .description("Compile a comprehensive analysis report")
            .uses_module("report-generator")
            .inputs("statistics", "charts")
            .outputs("report_url")
            .build()
        )
        .entry_node("load-data")
        .build()
    )

    # ================================================================
    # Workflow 2: Quick Summary
    # ================================================================
    quick_summary_workflow = (
        WorkflowBuilder("quick-summary")
        .description("Fast summary statistics without detailed analysis")
        .add_node(
            NodeBuilder("load-data")
            .description("Load data from specified source")
            .uses_module("data-loader")
            .inputs("source_type", "source_path")
            .outputs("data")
            .next_nodes("calculate-summary")
            .build()
        )
        .add_node(
            NodeBuilder("calculate-summary")
            .description("Calculate basic summary statistics")
            .uses_module("stats-calculator")
            .inputs("data")
            .outputs("statistics")
            .build()
        )
        .entry_node("load-data")
        .build()
    )

    # ================================================================
    # Workflow 3: Data Validation
    # ================================================================
    validation_workflow = (
        WorkflowBuilder("validate-data")
        .description("Validate data quality and schema compliance")
        .add_node(
            NodeBuilder("load-data")
            .description("Load data from specified source")
            .uses_module("data-loader")
            .inputs("source_type", "source_path")
            .outputs("data")
            .next_nodes("check-schema", "check-quality")
            .build()
        )
        .add_node(
            NodeBuilder("check-schema")
            .description("Validate data schema and structure")
            .uses_module("schema-validator")
            .inputs("data")
            .outputs("schema_valid", "schema_errors")
            .next_nodes("generate-validation-report")
            .build()
        )
        .add_node(
            NodeBuilder("check-quality")
            .description("Assess data quality metrics")
            .uses_module("quality-checker")
            .inputs("data")
            .outputs("quality_scores", "quality_issues")
            .next_nodes("generate-validation-report")
            .build()
        )
        .add_node(
            NodeBuilder("generate-validation-report")
            .description("Create validation report with findings")
            .uses_module("report-generator")
            .inputs("schema_valid", "schema_errors", "quality_scores", "quality_issues")
            .outputs("report_url")
            .build()
        )
        .entry_node("load-data")
        .build()
    )

    # ================================================================
    # Create Agent with All Workflows
    # ================================================================
    agent = (
        AgentBuilder("data-analyst")
        .description(
            "Comprehensive data analysis agent supporting full analysis, "
            "quick summaries, and data validation workflows"
        )
        .version("2.0.0")
        .add_module(data_loader)
        .add_module(data_cleaner)
        .add_module(stats_calculator)
        .add_module(visualizer)
        .add_module(report_generator)
        .add_module(schema_validator)
        .add_module(quality_checker)
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
    print(f"\nCreated agent: {agent.name} v{agent.version}")
    print(f"  Description: {agent.description}")
    print(f"  Modules: {len(agent.modules)}")
    print(f"  Workflows: {len(agent.workflows)}")

    # Display workflow details
    print("\nWorkflow Details:")
    for i, workflow in enumerate(agent.workflows, 1):
        print(f"\n  {i}. {workflow.name}")
        print(f"     Description: {workflow.description}")
        print(f"     Nodes: {len(workflow.nodes)}")
        for node in workflow.nodes:
            next_info = f" -> {', '.join(node.next_nodes)}" if node.next_nodes else ""
            print(f"       - {node.name}{next_info}")

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
    output_file = "data_analyst_agent.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(yaml_output)

    print(f"Exported to {output_file}")

    # Display YAML (truncated for readability)
    print("\n" + "=" * 70)
    print("Generated YAML (preview):")
    print("=" * 70)
    lines = yaml_output.split("\n")
    preview_lines = min(40, len(lines))
    print("\n".join(lines[:preview_lines]))
    if len(lines) > preview_lines:
        print(f"\n... ({len(lines) - preview_lines} more lines)")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  - Agents can have multiple workflows for different use cases")
    print("  - Each workflow can have a different number of nodes")
    print("  - Nodes reference modules, prompts, or tools")
    print(
        f"  - This agent has {sum(len(w.nodes) for w in agent.workflows)} "
        f"total nodes across {len(agent.workflows)} workflows"
    )

    return 0


if __name__ == "__main__":
    exit(main())
