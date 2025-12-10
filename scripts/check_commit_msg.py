#!/usr/bin/env python3
"""
Commit message format validator.

This script validates that commit messages follow the Conventional Commits
specification with project-specific scope requirements.

Usage:
    python scripts/check_commit_msg.py [commit_msg_file]

If no file is provided, reads from .git/COMMIT_EDITMSG.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

# Valid commit types (Conventional Commits + extensions)
TYPES = frozenset(
    [
        "feat",  # New feature
        "fix",  # Bug fix
        "docs",  # Documentation
        "style",  # Formatting (no logic change)
        "refactor",  # Refactoring (no behavior change)
        "perf",  # Performance improvement
        "test",  # Test-related
        "build",  # Build system
        "ci",  # CI configuration
        "chore",  # Misc (no src/test impact)
        "revert",  # Revert changes
    ]
)

# Valid scopes organized by category
SCOPES = frozenset(
    [
        # Architecture layers
        "domain",
        "app",
        "infra",
        "interface",
        # Feature modules
        "chat",
        "translation",
        "image",
        "speech",
        "video",
        "music",
        "travel",
        "presentation",
        "history",
        "settings",
        "counseling",
        # Technical components
        "provider",
        "storage",
        "middleware",
        "events",
        "errors",
        "logging",
        "types",
        "rust",
        "deps",
        # Special
        "release",
        "security",
    ]
)

# Maximum lengths
MAX_SUBJECT_LENGTH = 72  # GitHub truncates at 72
RECOMMENDED_SUBJECT_LENGTH = 50  # Best practice

# Commit message pattern
# Format: type(scope)!: subject
# - type: required, one of TYPES
# - scope: optional, one of SCOPES
# - !: optional, indicates breaking change
# - subject: required, lowercase start, no period at end
COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)"  # type
    r"(?:\((?P<scope>[a-z_-]+)\))?"  # optional scope
    r"(?P<breaking>!)?"  # optional breaking change indicator
    r": "  # separator
    r"(?P<subject>.+)$"  # subject
)

# =============================================================================
# Validation Functions
# =============================================================================


def validate_first_line(line: str) -> tuple[bool, list[str]]:
    """
    Validate the first line of the commit message.

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors: list[str] = []

    # Check overall format
    match = COMMIT_PATTERN.match(line)
    if not match:
        errors.append(
            f"Invalid format: '{line}'\n"
            f"Expected: <type>(<scope>): <subject>\n"
            f"Example: feat(chat): add streaming support"
        )
        return False, errors

    commit_type = match.group("type")
    scope = match.group("scope")
    subject = match.group("subject")

    # Validate type
    if commit_type not in TYPES:
        errors.append(
            f"Invalid type: '{commit_type}'\n" f"Valid types: {', '.join(sorted(TYPES))}"
        )

    # Validate scope (if provided)
    if scope and scope not in SCOPES:
        errors.append(
            f"Invalid scope: '{scope}'\n"
            f"Valid scopes: {', '.join(sorted(SCOPES))}"
        )

    # Validate subject
    if subject:
        # Check if subject starts with lowercase
        if subject[0].isupper():
            errors.append("Subject should start with lowercase letter")

        # Check if subject ends with period
        if subject.endswith("."):
            errors.append("Subject should not end with a period")

        # Check subject length
        if len(line) > MAX_SUBJECT_LENGTH:
            errors.append(
                f"First line is too long ({len(line)} > {MAX_SUBJECT_LENGTH} chars)"
            )
        elif len(line) > RECOMMENDED_SUBJECT_LENGTH:
            # This is a warning, not an error
            pass

    return len(errors) == 0, errors


def validate_body(lines: list[str]) -> tuple[bool, list[str]]:
    """
    Validate the body of the commit message.

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors: list[str] = []

    if len(lines) < 2:
        # No body, that's fine
        return True, errors

    # Check for blank line after subject
    if lines[1].strip():
        errors.append("Second line should be blank (separating subject from body)")

    # Check body line lengths (soft limit of 72 chars)
    for i, line in enumerate(lines[2:], start=3):
        if len(line) > 100:  # Hard limit
            errors.append(f"Line {i} is too long ({len(line)} > 100 chars)")

    return len(errors) == 0, errors


def validate_commit_message(message: str) -> tuple[bool, list[str]]:
    """
    Validate a complete commit message.

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    lines = message.strip().split("\n")

    if not lines or not lines[0].strip():
        return False, ["Empty commit message"]

    all_errors: list[str] = []

    # Validate first line
    valid, errors = validate_first_line(lines[0])
    all_errors.extend(errors)

    # Validate body
    valid_body, body_errors = validate_body(lines)
    all_errors.extend(body_errors)

    return len(all_errors) == 0, all_errors


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """
    Main entry point for the commit message validator.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Get commit message file path
    if len(sys.argv) > 1:
        commit_msg_file = Path(sys.argv[1])
    else:
        commit_msg_file = Path(".git/COMMIT_EDITMSG")

    # Read commit message
    try:
        message = commit_msg_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: Commit message file not found: {commit_msg_file}")
        return 1
    except OSError as e:
        print(f"Error reading commit message: {e}")
        return 1

    # Skip merge commits
    if message.startswith("Merge"):
        return 0

    # Skip revert commits (auto-generated by git)
    if message.startswith("Revert"):
        return 0

    # Validate commit message
    valid, errors = validate_commit_message(message)

    if not valid:
        print("=" * 60)
        print("COMMIT MESSAGE VALIDATION FAILED")
        print("=" * 60)
        print()
        for error in errors:
            print(f"  - {error}")
        print()
        print("-" * 60)
        print("Commit message format:")
        print("  <type>(<scope>): <subject>")
        print()
        print("  <body>")
        print()
        print("  <footer>")
        print("-" * 60)
        print(f"Types: {', '.join(sorted(TYPES))}")
        print(f"Scopes: {', '.join(sorted(SCOPES))}")
        print("-" * 60)
        print("Examples:")
        print("  feat(chat): add streaming support")
        print("  fix(storage): prevent memory leak")
        print("  docs(api): update usage examples")
        print("=" * 60)
        return 1

    print("Commit message validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
