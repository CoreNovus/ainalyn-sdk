"""
Builder error aliases for backward compatibility.

This module provides backward-compatible aliases to domain errors.
New code should import from ainalyn.domain.errors instead.

⚠️ DEPRECATED ⚠️
These error classes are maintained for backward compatibility only.
They are aliases to domain errors and will be removed in a future version.

Use ainalyn.domain.errors instead:
- MissingFieldError (replaces MissingRequiredFieldError)
- InvalidFormatError (replaces InvalidValueError)
- ReferenceError (replaces InvalidReferenceError)
- DuplicateError (replaces DuplicateNameError)
- EmptyCollectionError
"""

from __future__ import annotations

from ainalyn.domain.errors import DefinitionError

# Alias for backward compatibility
BuilderError = DefinitionError


# Import domain errors
from ainalyn.domain.errors import (
    DuplicateError,
    EmptyCollectionError,
    InvalidFormatError,
    MissingFieldError,
    ReferenceError,
)

# Legacy aliases for backward compatibility
# Deprecated: Use domain errors directly
MissingRequiredFieldError = MissingFieldError
InvalidValueError = InvalidFormatError
InvalidReferenceError = ReferenceError
DuplicateNameError = DuplicateError

# Re-export for compatibility
__all__ = [
    "BuilderError",
    "MissingRequiredFieldError",
    "InvalidValueError",
    "InvalidReferenceError",
    "DuplicateNameError",
    "EmptyCollectionError",
]
