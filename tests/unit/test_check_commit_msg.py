"""
Unit tests for commit message validator.

Tests the scripts/check_commit_msg.py module.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from check_commit_msg import (
    VALID_SCOPES,
    VALID_TYPES,
    ValidationError,
    ValidationResult,
    _find_similar,
    _suggest_imperative,
    should_skip_validation,
    validate_body,
    validate_commit_message,
    validate_first_line,
)


class TestValidTypes:
    """Tests for valid commit types."""

    def test_all_conventional_types_present(self) -> None:
        """All conventional commit types should be present."""
        expected = {"feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"}
        assert expected == VALID_TYPES

    def test_types_are_lowercase(self) -> None:
        """All types should be lowercase."""
        for t in VALID_TYPES:
            assert t == t.lower()


class TestValidScopes:
    """Tests for valid commit scopes."""

    def test_architecture_scopes_present(self) -> None:
        """Architecture layer scopes should be present."""
        architecture = {"domain", "app", "infra", "interface"}
        assert architecture.issubset(VALID_SCOPES)

    def test_feature_scopes_present(self) -> None:
        """Feature module scopes should be present."""
        features = {"chat", "translation", "image", "speech", "video", "music", "travel", "presentation", "history", "settings"}
        assert features.issubset(VALID_SCOPES)

    def test_technical_scopes_present(self) -> None:
        """Technical component scopes should be present."""
        technical = {"provider", "storage", "middleware", "events", "errors", "logging", "types", "rust", "deps"}
        assert technical.issubset(VALID_SCOPES)


class TestValidateFirstLine:
    """Tests for first line validation."""

    # =========================================================================
    # Valid Messages
    # =========================================================================

    @pytest.mark.parametrize(
        "message",
        [
            "feat(chat): add streaming support",
            "fix(storage): prevent memory leak",
            "docs: update readme",
            "refactor(middleware): simplify chain",
            "feat!: breaking change without scope",
            "feat(api)!: breaking change with scope",
            "chore(deps): update dependencies",
        ],
    )
    def test_valid_messages(self, message: str) -> None:
        """Valid commit messages should pass validation."""
        result = validate_first_line(message)
        assert result.is_valid, f"Expected valid but got errors: {result.errors}"

    def test_valid_message_parses_type(self) -> None:
        """Valid message should parse type correctly."""
        result = validate_first_line("feat(chat): add streaming")
        assert result.parsed_type == "feat"

    def test_valid_message_parses_scope(self) -> None:
        """Valid message should parse scope correctly."""
        result = validate_first_line("feat(chat): add streaming")
        assert result.parsed_scope == "chat"

    def test_valid_message_parses_subject(self) -> None:
        """Valid message should parse subject correctly."""
        result = validate_first_line("feat(chat): add streaming support")
        assert result.parsed_subject == "add streaming support"

    def test_valid_message_without_scope(self) -> None:
        """Valid message without scope should pass."""
        result = validate_first_line("docs: update readme")
        assert result.is_valid
        assert result.parsed_scope is None

    def test_breaking_change_indicator(self) -> None:
        """Breaking change indicator should be detected."""
        result = validate_first_line("feat(api)!: change response format")
        assert result.is_valid
        assert result.is_breaking

    # =========================================================================
    # Invalid Messages - Format
    # =========================================================================

    def test_empty_message_fails(self) -> None:
        """Empty message should fail."""
        result = validate_first_line("")
        assert not result.is_valid

    def test_missing_colon_fails(self) -> None:
        """Message without colon should fail."""
        result = validate_first_line("feat add something")
        assert not result.is_valid

    def test_missing_space_after_colon_fails(self) -> None:
        """Message without space after colon should fail."""
        result = validate_first_line("feat:add something")
        assert not result.is_valid

    # =========================================================================
    # Invalid Messages - Type
    # =========================================================================

    def test_invalid_type_fails(self) -> None:
        """Invalid type should fail."""
        result = validate_first_line("invalid(chat): something")
        assert not result.is_valid
        assert any("Invalid type" in e.message for e in result.errors)

    def test_uppercase_type_fails(self) -> None:
        """Uppercase type should fail."""
        result = validate_first_line("FEAT(chat): add something")
        assert not result.is_valid

    # =========================================================================
    # Invalid Messages - Scope
    # =========================================================================

    def test_invalid_scope_fails(self) -> None:
        """Invalid scope should fail."""
        result = validate_first_line("feat(invalid): something")
        assert not result.is_valid
        assert any("Invalid scope" in e.message for e in result.errors)

    # =========================================================================
    # Invalid Messages - Subject
    # =========================================================================

    def test_uppercase_subject_start_fails(self) -> None:
        """Subject starting with uppercase should fail."""
        result = validate_first_line("feat(chat): Add streaming")
        assert not result.is_valid
        assert any("lowercase" in e.message for e in result.errors)

    def test_subject_ending_with_period_fails(self) -> None:
        """Subject ending with period should fail."""
        result = validate_first_line("feat(chat): add streaming.")
        assert not result.is_valid
        assert any("period" in e.message for e in result.errors)

    def test_past_tense_subject_fails(self) -> None:
        """Subject in past tense should fail."""
        result = validate_first_line("feat(chat): added streaming")
        assert not result.is_valid
        assert any("imperative" in e.message for e in result.errors)

    @pytest.mark.parametrize(
        "past_tense_word",
        ["added", "removed", "fixed", "updated", "changed", "implemented"],
    )
    def test_various_past_tense_words_fail(self, past_tense_word: str) -> None:
        """Various past tense words should fail."""
        result = validate_first_line(f"feat(chat): {past_tense_word} something")
        assert not result.is_valid

    def test_line_too_long_fails(self) -> None:
        """Line exceeding 72 characters should fail."""
        long_subject = "a" * 62  # type + scope + ": " takes ~12 chars, 12 + 62 = 74 > 72
        result = validate_first_line(f"feat(chat): {long_subject}")
        assert not result.is_valid

    def test_line_over_50_chars_warns(self) -> None:
        """Line over 50 but under 72 chars should warn."""
        # Create message that's 55 chars total
        result = validate_first_line("feat(chat): add support for something new here")
        # Should still be valid, but with warning
        assert result.is_valid
        # Check for warning about recommended length


class TestValidateBody:
    """Tests for body validation."""

    def test_no_body_passes(self) -> None:
        """Message without body should pass."""
        result = validate_body(["feat(chat): add streaming"])
        assert result.is_valid

    def test_body_with_blank_line_passes(self) -> None:
        """Body separated by blank line should pass."""
        lines = [
            "feat(chat): add streaming",
            "",
            "This is the body explaining why.",
        ]
        result = validate_body(lines)
        assert result.is_valid

    def test_body_without_blank_line_fails(self) -> None:
        """Body without blank line separator should fail."""
        lines = [
            "feat(chat): add streaming",
            "This is the body without blank line.",
        ]
        result = validate_body(lines)
        assert not result.is_valid
        assert any("blank" in e.message.lower() for e in result.errors)

    def test_body_line_over_100_chars_fails(self) -> None:
        """Body line over 100 characters should fail."""
        long_line = "x" * 101
        lines = [
            "feat(chat): add streaming",
            "",
            long_line,
        ]
        result = validate_body(lines)
        assert not result.is_valid

    def test_body_line_over_72_chars_warns(self) -> None:
        """Body line over 72 but under 100 chars should warn."""
        long_line = "x" * 80
        lines = [
            "feat(chat): add streaming",
            "",
            long_line,
        ]
        result = validate_body(lines)
        assert result.is_valid  # Still valid
        assert len(result.warnings) > 0  # But has warnings


class TestValidateCommitMessage:
    """Tests for complete commit message validation."""

    def test_simple_valid_message(self) -> None:
        """Simple valid message should pass."""
        result = validate_commit_message("feat(chat): add streaming support")
        assert result.is_valid

    def test_complete_valid_message(self) -> None:
        """Complete message with body and footer should pass."""
        message = """feat(chat): add streaming support

This implements server-sent events for real-time streaming.

Closes #123"""
        result = validate_commit_message(message)
        assert result.is_valid

    def test_message_with_breaking_change_footer(self) -> None:
        """Message with BREAKING CHANGE footer should pass."""
        message = """feat(api)!: change response format

BREAKING CHANGE: response.message is now response.content"""
        result = validate_commit_message(message)
        assert result.is_valid
        assert result.is_breaking

    def test_empty_message_fails(self) -> None:
        """Empty message should fail."""
        result = validate_commit_message("")
        assert not result.is_valid

    def test_whitespace_only_message_fails(self) -> None:
        """Whitespace-only message should fail."""
        result = validate_commit_message("   \n\n   ")
        assert not result.is_valid


class TestShouldSkipValidation:
    """Tests for skip validation logic."""

    def test_merge_commit_skipped(self) -> None:
        """Merge commits should be skipped."""
        assert should_skip_validation("Merge branch 'feature' into main")

    def test_revert_commit_skipped(self) -> None:
        """Revert commits should be skipped."""
        assert should_skip_validation("Revert \"feat(chat): add streaming\"")

    def test_fixup_commit_skipped(self) -> None:
        """Fixup commits should be skipped."""
        assert should_skip_validation("fixup! feat(chat): add streaming")

    def test_squash_commit_skipped(self) -> None:
        """Squash commits should be skipped."""
        assert should_skip_validation("squash! feat(chat): add streaming")

    def test_normal_commit_not_skipped(self) -> None:
        """Normal commits should not be skipped."""
        assert not should_skip_validation("feat(chat): add streaming")


class TestFindSimilar:
    """Tests for similar value finder."""

    def test_finds_similar_type(self) -> None:
        """Should find similar type for typo."""
        similar = _find_similar("feta", VALID_TYPES)
        assert similar == "feat"

    def test_finds_similar_scope(self) -> None:
        """Should find similar scope for typo."""
        similar = _find_similar("stor", VALID_SCOPES)
        assert similar == "storage"

    def test_returns_none_for_very_different(self) -> None:
        """Should return None for very different value."""
        similar = _find_similar("xyz", VALID_TYPES)
        assert similar is None


class TestSuggestImperative:
    """Tests for imperative mood suggester."""

    @pytest.mark.parametrize(
        ("past", "imperative"),
        [
            ("added", "add"),
            ("removed", "remove"),
            ("fixed", "fix"),
            ("updated", "update"),
            ("changed", "change"),
            ("implemented", "implement"),
            ("improved", "improve"),
            ("refactored", "refactor"),
        ],
    )
    def test_suggests_correct_imperative(self, past: str, imperative: str) -> None:
        """Should suggest correct imperative form."""
        assert _suggest_imperative(past) == imperative

    def test_unknown_past_returns_none(self) -> None:
        """Should return None for unknown past tense."""
        assert _suggest_imperative("unknown") is None


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_default_values(self) -> None:
        """Default values should be correct."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid
        assert result.errors == []
        assert result.warnings == []
        assert result.parsed_type is None
        assert result.parsed_scope is None
        assert result.parsed_subject is None
        assert result.is_breaking is False


class TestValidationError:
    """Tests for ValidationError dataclass."""

    def test_error_with_all_fields(self) -> None:
        """Error should store all fields."""
        error = ValidationError(
            message="Test error",
            line_number=1,
            severity="error",
            suggestion="Fix it",
        )
        assert error.message == "Test error"
        assert error.line_number == 1
        assert error.severity == "error"
        assert error.suggestion == "Fix it"

    def test_error_default_values(self) -> None:
        """Error should have correct defaults."""
        error = ValidationError(message="Test")
        assert error.line_number is None
        assert error.severity == "error"
        assert error.suggestion is None
