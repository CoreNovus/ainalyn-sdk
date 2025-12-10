#!/usr/bin/env python3
"""
Commit message format validator.

This script validates that commit messages follow the Conventional Commits
specification with project-specific scope requirements as defined in
docs/COMMIT_CONVENTIONS.md.

Usage:
    python scripts/check_commit_msg.py [commit_msg_file]
    python scripts/check_commit_msg.py --help
    python scripts/check_commit_msg.py --validate "feat(chat): add streaming"

If no file is provided, reads from .git/COMMIT_EDITMSG.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


# =============================================================================
# Configuration - Based on docs/COMMIT_CONVENTIONS.md
# =============================================================================

class CommitType(str, Enum):
    """Valid commit types (Conventional Commits + extensions)."""

    FEAT = "feat"  # New feature
    FIX = "fix"  # Bug fix
    DOCS = "docs"  # Documentation
    STYLE = "style"  # Formatting (no logic change)
    REFACTOR = "refactor"  # Refactoring (no behavior change)
    PERF = "perf"  # Performance improvement
    TEST = "test"  # Test-related
    BUILD = "build"  # Build system
    CI = "ci"  # CI configuration
    CHORE = "chore"  # Misc (no src/test impact)
    REVERT = "revert"  # Revert changes


# Type descriptions for help messages
TYPE_DESCRIPTIONS: dict[str, str] = {
    "feat": "New feature",
    "fix": "Bug fix",
    "docs": "Documentation changes",
    "style": "Formatting (no logic change)",
    "refactor": "Refactoring (no behavior change)",
    "perf": "Performance improvement",
    "test": "Test-related changes",
    "build": "Build system changes",
    "ci": "CI configuration changes",
    "chore": "Misc (no src/test impact)",
    "revert": "Revert previous changes",
}

# Valid scopes organized by category
SCOPES_BY_CATEGORY: dict[str, list[str]] = {
    "Architecture layers": ["domain", "app", "infra", "interface"],
    "Feature modules": [
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
    ],
    "Technical components": [
        "provider",
        "storage",
        "middleware",
        "events",
        "errors",
        "logging",
        "types",
        "rust",
        "deps",
    ],
    "Special": ["release", "security", "api"],
}

# Flatten scopes for validation
VALID_TYPES: frozenset[str] = frozenset(t.value for t in CommitType)
VALID_SCOPES: frozenset[str] = frozenset(
    scope for scopes in SCOPES_BY_CATEGORY.values() for scope in scopes
)

# Length constraints
MAX_SUBJECT_LENGTH = 72  # GitHub truncates at 72
RECOMMENDED_SUBJECT_LENGTH = 50  # Best practice
MAX_BODY_LINE_LENGTH = 100  # Hard limit for body lines
RECOMMENDED_BODY_LINE_LENGTH = 72  # Soft limit

# Common imperative verbs (for suggestions)
IMPERATIVE_VERBS: frozenset[str] = frozenset([
    "add", "implement", "introduce", "create",
    "remove", "delete", "drop",
    "fix", "resolve", "correct",
    "update", "upgrade", "bump",
    "improve", "enhance", "optimize",
    "refactor", "restructure", "reorganize",
    "rename", "move",
    "simplify", "streamline",
    "extract", "separate",
    "merge", "combine", "consolidate",
    "change", "modify", "adjust",
    "enable", "disable",
    "support", "allow",
    "prevent", "avoid",
    "replace", "switch",
])

# Past tense patterns to detect (should use imperative)
PAST_TENSE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^(added|removed|fixed|updated|changed|modified)\b", re.IGNORECASE),
    re.compile(r"^(implemented|introduced|created|deleted)\b", re.IGNORECASE),
    re.compile(r"^(improved|enhanced|optimized|refactored)\b", re.IGNORECASE),
]

# Commit message pattern
# Format: type(scope)!: subject
COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)"  # type (required)
    r"(?:\((?P<scope>[a-z][a-z0-9_-]*)\))?"  # scope (optional)
    r"(?P<breaking>!)?"  # breaking change indicator (optional)
    r": "  # separator (required)
    r"(?P<subject>.+)$"  # subject (required)
)

# Footer patterns
ISSUE_PATTERN = re.compile(
    r"^(Closes|Fixes|Resolves|Refs?|Related to)\s+#\d+",
    re.IGNORECASE,
)
BREAKING_CHANGE_PATTERN = re.compile(r"^BREAKING CHANGE:", re.IGNORECASE)
CO_AUTHOR_PATTERN = re.compile(r"^Co-authored-by:\s+.+\s+<.+>$", re.IGNORECASE)


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ValidationError:
    """Represents a validation error."""

    message: str
    line_number: int | None = None
    severity: str = "error"  # "error" or "warning"
    suggestion: str | None = None


@dataclass
class ValidationResult:
    """Result of commit message validation."""

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    parsed_type: str | None = None
    parsed_scope: str | None = None
    parsed_subject: str | None = None
    is_breaking: bool = False


# =============================================================================
# Validation Functions
# =============================================================================


def validate_first_line(line: str) -> ValidationResult:
    """
    Validate the first line (header) of the commit message.

    Args:
        line: The first line of the commit message

    Returns:
        ValidationResult with errors and parsed components
    """
    result = ValidationResult(is_valid=True)
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    # Check if line is empty
    if not line.strip():
        errors.append(ValidationError(
            message="First line cannot be empty",
            line_number=1,
        ))
        result.is_valid = False
        result.errors = errors
        return result

    # Check overall format
    match = COMMIT_PATTERN.match(line)
    if not match:
        # Try to give a helpful error message
        if ":" not in line:
            suggestion = "Missing colon separator. Format: type(scope): subject"
        elif not line.split(":")[0].strip():
            suggestion = "Missing type before colon"
        else:
            suggestion = "Format: <type>(<scope>): <subject>"

        errors.append(ValidationError(
            message=f"Invalid commit message format",
            line_number=1,
            suggestion=suggestion,
        ))
        result.is_valid = False
        result.errors = errors
        return result

    # Extract components
    commit_type = match.group("type")
    scope = match.group("scope")
    subject = match.group("subject")
    is_breaking = match.group("breaking") == "!"

    result.parsed_type = commit_type
    result.parsed_scope = scope
    result.parsed_subject = subject
    result.is_breaking = is_breaking

    # Validate type
    if commit_type not in VALID_TYPES:
        similar = _find_similar(commit_type, VALID_TYPES)
        suggestion = f"Did you mean: {similar}?" if similar else None
        errors.append(ValidationError(
            message=f"Invalid type: '{commit_type}'",
            line_number=1,
            suggestion=suggestion or f"Valid types: {', '.join(sorted(VALID_TYPES))}",
        ))

    # Validate scope (if provided)
    if scope and scope not in VALID_SCOPES:
        similar = _find_similar(scope, VALID_SCOPES)
        suggestion = f"Did you mean: {similar}?" if similar else None
        errors.append(ValidationError(
            message=f"Invalid scope: '{scope}'",
            line_number=1,
            suggestion=suggestion or f"Valid scopes: {', '.join(sorted(VALID_SCOPES))}",
        ))

    # Validate subject
    if subject:
        # Check if subject starts with uppercase
        if subject[0].isupper():
            errors.append(ValidationError(
                message="Subject should start with lowercase letter",
                line_number=1,
                suggestion=f"Change to: {subject[0].lower()}{subject[1:]}",
            ))

        # Check if subject ends with period
        if subject.endswith("."):
            errors.append(ValidationError(
                message="Subject should not end with a period",
                line_number=1,
                suggestion=f"Remove trailing period: {subject[:-1]}",
            ))

        # Check for past tense
        for pattern in PAST_TENSE_PATTERNS:
            if pattern.match(subject):
                first_word = subject.split()[0].lower()
                imperative = _suggest_imperative(first_word)
                errors.append(ValidationError(
                    message="Subject should use imperative mood (not past tense)",
                    line_number=1,
                    suggestion=f"Change '{first_word}' to '{imperative}'" if imperative else None,
                ))
                break

        # Check subject length
        if len(line) > MAX_SUBJECT_LENGTH:
            errors.append(ValidationError(
                message=f"First line is too long ({len(line)} > {MAX_SUBJECT_LENGTH} chars)",
                line_number=1,
            ))
        elif len(line) > RECOMMENDED_SUBJECT_LENGTH:
            warnings.append(ValidationError(
                message=f"First line is longer than recommended ({len(line)} > {RECOMMENDED_SUBJECT_LENGTH} chars)",
                line_number=1,
                severity="warning",
            ))

    result.is_valid = len(errors) == 0
    result.errors = errors
    result.warnings = warnings
    return result


def validate_body(lines: list[str]) -> ValidationResult:
    """
    Validate the body of the commit message.

    Args:
        lines: All lines of the commit message

    Returns:
        ValidationResult with body-related errors
    """
    result = ValidationResult(is_valid=True)
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    if len(lines) < 2:
        # No body, that's fine
        return result

    # Check for blank line after subject
    if lines[1].strip():
        errors.append(ValidationError(
            message="Second line must be blank (separates subject from body)",
            line_number=2,
        ))

    # Check body line lengths
    for i, line in enumerate(lines[2:], start=3):
        # Skip footer lines (they often contain URLs)
        if ISSUE_PATTERN.match(line) or BREAKING_CHANGE_PATTERN.match(line):
            continue
        if CO_AUTHOR_PATTERN.match(line):
            continue

        if len(line) > MAX_BODY_LINE_LENGTH:
            errors.append(ValidationError(
                message=f"Line {i} is too long ({len(line)} > {MAX_BODY_LINE_LENGTH} chars)",
                line_number=i,
            ))
        elif len(line) > RECOMMENDED_BODY_LINE_LENGTH:
            warnings.append(ValidationError(
                message=f"Line {i} exceeds recommended length ({len(line)} > {RECOMMENDED_BODY_LINE_LENGTH} chars)",
                line_number=i,
                severity="warning",
            ))

    result.is_valid = len(errors) == 0
    result.errors = errors
    result.warnings = warnings
    return result


def validate_footer(lines: list[str]) -> ValidationResult:
    """
    Validate the footer of the commit message.

    Args:
        lines: All lines of the commit message

    Returns:
        ValidationResult with footer-related errors/warnings
    """
    result = ValidationResult(is_valid=True)
    warnings: list[ValidationError] = []

    # Find footer section (after blank line in body)
    footer_start = None
    for i, line in enumerate(lines[2:], start=2):
        if not line.strip():
            footer_start = i + 1
            break

    if footer_start is None or footer_start >= len(lines):
        return result

    # Check footer format
    for i, line in enumerate(lines[footer_start:], start=footer_start + 1):
        if not line.strip():
            continue

        # Valid footer patterns
        is_valid_footer = (
            ISSUE_PATTERN.match(line)
            or BREAKING_CHANGE_PATTERN.match(line)
            or CO_AUTHOR_PATTERN.match(line)
            or line.startswith("Signed-off-by:")
        )

        if not is_valid_footer and line.strip():
            # It might be continuation of breaking change description
            pass

    return result


def validate_commit_message(message: str) -> ValidationResult:
    """
    Validate a complete commit message.

    Args:
        message: The full commit message text

    Returns:
        ValidationResult with all validation information
    """
    # Handle empty message
    if not message or not message.strip():
        return ValidationResult(
            is_valid=False,
            errors=[ValidationError(message="Empty commit message", line_number=1)],
        )

    lines = message.split("\n")

    # Remove trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return ValidationResult(
            is_valid=False,
            errors=[ValidationError(message="Empty commit message", line_number=1)],
        )

    # Validate first line
    header_result = validate_first_line(lines[0])

    # Validate body
    body_result = validate_body(lines)

    # Validate footer
    footer_result = validate_footer(lines)

    # Combine results
    all_errors = header_result.errors + body_result.errors + footer_result.errors
    all_warnings = header_result.warnings + body_result.warnings + footer_result.warnings

    return ValidationResult(
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
        parsed_type=header_result.parsed_type,
        parsed_scope=header_result.parsed_scope,
        parsed_subject=header_result.parsed_subject,
        is_breaking=header_result.is_breaking,
    )


# =============================================================================
# Helper Functions
# =============================================================================


def _find_similar(value: str, valid_values: frozenset[str]) -> str | None:
    """Find similar value from valid values using simple distance."""
    best_match = None
    best_distance = float("inf")

    for valid in valid_values:
        # Simple prefix matching
        if valid.startswith(value[:2]) or value.startswith(valid[:2]):
            distance = abs(len(valid) - len(value))
            if distance < best_distance:
                best_distance = distance
                best_match = valid

    return best_match if best_distance <= 3 else None


def _suggest_imperative(past_tense: str) -> str | None:
    """Suggest imperative form for common past tense verbs."""
    mapping = {
        "added": "add",
        "removed": "remove",
        "deleted": "delete",
        "fixed": "fix",
        "updated": "update",
        "changed": "change",
        "modified": "modify",
        "implemented": "implement",
        "introduced": "introduce",
        "created": "create",
        "improved": "improve",
        "enhanced": "enhance",
        "optimized": "optimize",
        "refactored": "refactor",
    }
    return mapping.get(past_tense.lower())


def should_skip_validation(message: str) -> bool:
    """Check if message should skip validation (merge, revert, etc.)."""
    first_line = message.split("\n")[0].strip()

    # Skip merge commits
    if first_line.startswith("Merge"):
        return True

    # Skip revert commits (auto-generated)
    if first_line.startswith("Revert"):
        return True

    # Skip fixup commits (will be squashed)
    if first_line.startswith("fixup!") or first_line.startswith("squash!"):
        return True

    # Skip amend commits
    if first_line.startswith("amend!"):
        return True

    return False


# =============================================================================
# Output Formatting
# =============================================================================


def format_error_output(result: ValidationResult, message: str) -> str:
    """Format validation errors for terminal output."""
    lines = message.split("\n")
    output_parts = []

    output_parts.append("=" * 60)
    output_parts.append("COMMIT MESSAGE VALIDATION FAILED")
    output_parts.append("=" * 60)
    output_parts.append("")

    # Show the commit message with line numbers
    output_parts.append("Your commit message:")
    output_parts.append("-" * 40)
    for i, line in enumerate(lines[:5], start=1):  # Show first 5 lines
        prefix = ">>>" if any(e.line_number == i for e in result.errors) else "   "
        output_parts.append(f"{prefix} {i}: {line}")
    if len(lines) > 5:
        output_parts.append(f"    ... ({len(lines) - 5} more lines)")
    output_parts.append("-" * 40)
    output_parts.append("")

    # Show errors
    output_parts.append("Errors:")
    for error in result.errors:
        line_info = f" (line {error.line_number})" if error.line_number else ""
        output_parts.append(f"  [X] {error.message}{line_info}")
        if error.suggestion:
            output_parts.append(f"    -> {error.suggestion}")
    output_parts.append("")

    # Show warnings
    if result.warnings:
        output_parts.append("Warnings:")
        for warning in result.warnings:
            line_info = f" (line {warning.line_number})" if warning.line_number else ""
            output_parts.append(f"  [!] {warning.message}{line_info}")
        output_parts.append("")

    # Show format help
    output_parts.append("-" * 60)
    output_parts.append("Expected format:")
    output_parts.append("  <type>(<scope>): <subject>")
    output_parts.append("")
    output_parts.append("  <body>")
    output_parts.append("")
    output_parts.append("  <footer>")
    output_parts.append("-" * 60)

    # Show valid types
    output_parts.append("Valid types:")
    for t in sorted(VALID_TYPES):
        desc = TYPE_DESCRIPTIONS.get(t, "")
        output_parts.append(f"  {t:10} - {desc}")
    output_parts.append("")

    # Show valid scopes (grouped)
    output_parts.append("Valid scopes:")
    for category, scopes in SCOPES_BY_CATEGORY.items():
        output_parts.append(f"  {category}: {', '.join(scopes)}")
    output_parts.append("")

    # Show examples
    output_parts.append("-" * 60)
    output_parts.append("Examples:")
    output_parts.append("  feat(chat): add streaming support")
    output_parts.append("  fix(storage): prevent memory leak")
    output_parts.append("  docs(api): update usage examples")
    output_parts.append("  refactor(middleware): simplify chain")
    output_parts.append("=" * 60)

    return "\n".join(output_parts)


def format_success_output(result: ValidationResult) -> str:
    """Format success message for terminal output."""
    parts = ["[OK] Commit message validation passed"]

    if result.warnings:
        parts.append("")
        parts.append("Warnings:")
        for warning in result.warnings:
            parts.append(f"  [!] {warning.message}")

    return "\n".join(parts)


# =============================================================================
# CLI Functions
# =============================================================================


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Validate commit message format according to project conventions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Validate .git/COMMIT_EDITMSG
  %(prog)s .git/COMMIT_EDITMSG       # Validate specific file
  %(prog)s --validate "feat: test"   # Validate string directly
  %(prog)s --list-types              # Show valid types
  %(prog)s --list-scopes             # Show valid scopes
        """,
    )

    parser.add_argument(
        "commit_msg_file",
        nargs="?",
        default=".git/COMMIT_EDITMSG",
        help="Path to commit message file (default: .git/COMMIT_EDITMSG)",
    )

    parser.add_argument(
        "--validate", "-v",
        metavar="MESSAGE",
        help="Validate a commit message string directly",
    )

    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List all valid commit types",
    )

    parser.add_argument(
        "--list-scopes",
        action="store_true",
        help="List all valid scopes",
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output errors (no success message)",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )

    return parser


def main() -> int:
    """
    Main entry point for the commit message validator.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Handle --list-types
    if args.list_types:
        print("Valid commit types:")
        for t in sorted(VALID_TYPES):
            desc = TYPE_DESCRIPTIONS.get(t, "")
            print(f"  {t:10} - {desc}")
        return 0

    # Handle --list-scopes
    if args.list_scopes:
        print("Valid scopes by category:")
        for category, scopes in SCOPES_BY_CATEGORY.items():
            print(f"\n{category}:")
            for scope in scopes:
                print(f"  {scope}")
        return 0

    # Get commit message
    if args.validate:
        message = args.validate
    else:
        commit_msg_file = Path(args.commit_msg_file)
        try:
            message = commit_msg_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"Error: Commit message file not found: {commit_msg_file}")
            return 1
        except OSError as e:
            print(f"Error reading commit message: {e}")
            return 1

    # Check if validation should be skipped
    if should_skip_validation(message):
        if not args.quiet:
            print("[OK] Skipping validation (merge/revert/fixup commit)")
        return 0

    # Validate commit message
    result = validate_commit_message(message)

    # Handle strict mode
    if args.strict and result.warnings:
        result.is_valid = False
        result.errors.extend(result.warnings)

    # Output results
    if not result.is_valid:
        print(format_error_output(result, message))
        return 1

    if not args.quiet:
        print(format_success_output(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
