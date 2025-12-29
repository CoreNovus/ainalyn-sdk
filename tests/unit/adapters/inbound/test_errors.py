"""Unit tests for builder errors."""

from __future__ import annotations

from ainalyn.adapters.inbound.errors import (
    BuilderError,
    DuplicateNameError,
    EmptyCollectionError,
    InvalidReferenceError,
    InvalidValueError,
    MissingRequiredFieldError,
)


class TestBuilderError:
    """Tests for BuilderError base class."""

    def test_builder_error_creation(self) -> None:
        """Test that BuilderError can be created with a message."""
        error = BuilderError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"

    def test_builder_error_is_exception(self) -> None:
        """Test that BuilderError is an Exception."""
        error = BuilderError("Test")
        assert isinstance(error, Exception)


class TestMissingRequiredFieldError:
    """Tests for MissingRequiredFieldError (alias to MissingFieldError)."""

    def test_missing_field_error_message(self) -> None:
        """Test the error message format."""
        error = MissingRequiredFieldError("name", "ModuleBuilder")
        # Domain error format
        expected = "Required field 'name' is missing or empty in ModuleBuilder"
        assert str(error) == expected
        assert error.field_name == "name"
        assert error.entity_type == "ModuleBuilder"

    def test_missing_field_error_is_builder_error(self) -> None:
        """Test inheritance."""
        error = MissingRequiredFieldError("version", "AgentBuilder")
        assert isinstance(error, BuilderError)


class TestInvalidValueError:
    """Tests for InvalidValueError."""

    def test_invalid_value_error_message(self) -> None:
        """Test the error message format."""
        error = InvalidValueError(
            "name",
            "Invalid-Name",
            "must be lowercase",
        )
        expected = "Invalid value for 'name': 'Invalid-Name'. must be lowercase"
        assert str(error) == expected
        assert error.field_name == "name"
        assert error.value == "Invalid-Name"
        assert error.constraint == "must be lowercase"

    def test_invalid_value_error_is_builder_error(self) -> None:
        """Test inheritance."""
        error = InvalidValueError("version", "1.x", "must be semver")
        assert isinstance(error, BuilderError)


class TestInvalidReferenceError:
    """Tests for InvalidReferenceError (alias to ReferenceError)."""

    def test_invalid_reference_error_message(self) -> None:
        """Test the error message format."""
        error = InvalidReferenceError("fetch", "module", "http-fetcher")
        # Domain error format
        expected = (
            "'fetch' references undefined module 'http-fetcher'. "
            "The module must be defined in the agent."
        )
        assert str(error) == expected
        assert error.source == "fetch"
        assert error.resource_type == "module"
        assert error.reference == "http-fetcher"

    def test_invalid_reference_error_is_builder_error(self) -> None:
        """Test inheritance."""
        error = InvalidReferenceError("process", "prompt", "analyzer")
        assert isinstance(error, BuilderError)


class TestDuplicateNameError:
    """Tests for DuplicateNameError."""

    def test_duplicate_name_error_message(self) -> None:
        """Test the error message format."""
        error = DuplicateNameError("node", "fetch", "workflow 'main'")
        expected = (
            "Duplicate node name 'fetch' in workflow 'main'. "
            "Each node must have a unique name within its scope."
        )
        assert str(error) == expected
        assert error.entity_type == "node"
        assert error.name == "fetch"
        assert error.scope == "workflow 'main'"

    def test_duplicate_name_error_is_builder_error(self) -> None:
        """Test inheritance."""
        error = DuplicateNameError("module", "http-fetcher", "agent 'my-agent'")
        assert isinstance(error, BuilderError)


class TestEmptyCollectionError:
    """Tests for EmptyCollectionError."""

    def test_empty_collection_error_message(self) -> None:
        """Test the error message format."""
        error = EmptyCollectionError("nodes", "Workflow 'main'")
        # Domain error format
        expected = "'Workflow 'main'' has no nodes. At least one node is required."
        assert str(error) == expected
        assert error.collection_name == "nodes"
        assert error.parent_name == "Workflow 'main'"

    def test_empty_collection_error_is_builder_error(self) -> None:
        """Test inheritance."""
        error = EmptyCollectionError("workflows", "Agent 'my-agent'")
        assert isinstance(error, BuilderError)
