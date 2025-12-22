"""
Command-line interface for Ainalyn SDK.

This module provides a lightweight CLI tool for validating and compiling
Agent Definitions from Python files.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:
    from ainalyn.domain.entities import AgentDefinition


def main() -> NoReturn:
    """
    Main entry point for the CLI.

    This function provides a simple command-line interface for:
    - Validating Agent Definitions
    - Compiling Agent Definitions to YAML

    Returns:
        NoReturn: This function always calls sys.exit().
    """
    parser = argparse.ArgumentParser(
        prog="ainalyn",
        description="Ainalyn SDK - Agent Definition Compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate an agent definition
  ainalyn validate agent.py

  # Compile an agent definition to YAML
  ainalyn compile agent.py -o output.yaml

  # Show version
  ainalyn --version
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate an Agent Definition",
    )
    validate_parser.add_argument(
        "file",
        type=Path,
        help="Path to Python file containing AgentDefinition",
    )

    # Compile command
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile an Agent Definition to YAML",
    )
    compile_parser.add_argument(
        "file",
        type=Path,
        help="Path to Python file containing AgentDefinition",
    )
    compile_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output YAML file path",
    )

    args = parser.parse_args()

    # Handle commands
    if args.command == "validate":
        sys.exit(_validate_command(args.file))
    elif args.command == "compile":
        sys.exit(_compile_command(args.file, args.output))
    else:
        parser.print_help()
        sys.exit(1)


def _get_version() -> str:
    """Get the SDK version."""
    try:
        from ainalyn._version import __version__

        return __version__
    except ImportError:
        return "unknown"


def _validate_command(file_path: Path) -> int:
    """
    Execute the validate command.

    Args:
        file_path: Path to the Python file containing AgentDefinition.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    # Load the definition
    definition = _load_definition(file_path)
    if definition is None:
        return 1

    # Import here to avoid circular imports
    from ainalyn.api import validate

    # Validate
    print(f"Validating {file_path}...")
    result = validate(definition)

    if result.is_valid:
        print("✓ Validation passed!")
        if result.has_warnings:
            print("\nWarnings:")
            for error in result.errors:
                if error.severity.value == "warning":
                    print(f"  {error.code}: {error.message}")
                    print(f"    Location: {error.path}")
        return 0
    else:
        print("✗ Validation failed!\n")
        print("Errors:")
        for error in result.errors:
            if error.severity.value == "error":
                print(f"  {error.code}: {error.message}")
                print(f"    Location: {error.path}")
        return 1


def _compile_command(file_path: Path, output_path: Path) -> int:
    """
    Execute the compile command.

    Args:
        file_path: Path to the Python file containing AgentDefinition.
        output_path: Path to write the compiled YAML file.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    # Load the definition
    definition = _load_definition(file_path)
    if definition is None:
        return 1

    # Import here to avoid circular imports
    from ainalyn.api import compile_agent

    # Compile
    print(f"Compiling {file_path}...")
    result = compile_agent(definition, output_path)

    if result.is_successful:
        print(f"✓ Successfully compiled to {output_path}")
        print("  Note: This file describes an Agent Definition for platform submission.")
        print("        Local compilation does NOT equal platform execution.")
        if result.validation_result.has_warnings:
            print("\nWarnings:")
            for error in result.validation_result.errors:
                if error.severity.value == "warning":
                    print(f"  {error.code}: {error.message}")
                    print(f"    Location: {error.path}")
        return 0
    else:
        print("✗ Compilation failed!\n")
        print("Errors:")
        for error in result.validation_result.errors:
            if error.severity.value == "error":
                print(f"  {error.code}: {error.message}")
                print(f"    Location: {error.path}")
        return 1


def _load_definition(file_path: Path) -> AgentDefinition | None:
    """
    Load an AgentDefinition from a Python file.

    This function executes the Python file and looks for a variable
    named 'agent' or 'definition' containing an AgentDefinition.

    Args:
        file_path: Path to the Python file.

    Returns:
        AgentDefinition | None: The loaded definition, or None if loading failed.
    """
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return None

    if file_path.suffix != ".py":
        print(f"Error: File must be a Python file (.py): {file_path}")
        return None

    try:
        # Execute the file
        namespace: dict[str, object] = {}
        with file_path.open() as f:
            code = compile(f.read(), str(file_path), "exec")
            exec(code, namespace)

        # Look for AgentDefinition
        definition = namespace.get("agent") or namespace.get("definition")
        if definition is None:
            print("Error: No 'agent' or 'definition' variable found in file")
            return None

        # Import here to avoid circular imports
        from ainalyn.domain.entities import AgentDefinition

        if not isinstance(definition, AgentDefinition):
            print(
                f"Error: Variable must be an AgentDefinition, "
                f"got {type(definition).__name__}"
            )
            return None

        return definition

    except Exception as e:
        print(f"Error loading file: {e}")
        return None


if __name__ == "__main__":
    main()
