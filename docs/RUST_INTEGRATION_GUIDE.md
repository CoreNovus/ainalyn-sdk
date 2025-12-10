# Rust Integration Guide

> This document describes the integration boundaries, usage scenarios, and development guidelines for Rust modules in the SDK.

## 1. Overview of Rust Integration Strategy

### 1.1 Why Use Rust

| Feature                | Pure Python         | Rust Module    | Reason for Choice           |
| ---------------------- | ------------------- | -------------- | --------------------------- |
| Token counting         | Slow, external deps | Fast, accurate | Performance critical        |
| Content filtering      | Feasible but slow   | Efficient      | Large-scale text handling   |
| Crypto/Signing         | Good existing libs  | Optional       | Python libraries are enough |
| General business logic | Preferred           | Not applicable | Maintainability first       |

### 1.2 Integration Boundary Principles

```
┌─────────────────────────────────────────────────────────┐
│                      Python Domain                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Interface / Application / Domain                │   │
│  │ - All business logic                           │   │
│  │ - All flow control                             │   │
│  │ - Data structure definitions                   │   │
│  └─────────────────────────────────────────────────┘   │
│                         ▲                               │
│                         │ Call                          │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Infrastructure Layer (Rust Binding)             │   │
│  │ - Python wrapper                                │   │
│  │ - Type conversion                               │   │
│  │ - Error translation                             │   │
│  └──────────────────────┬──────────────────────────┘   │
└─────────────────────────┼──────────────────────────────┘
                          │ FFI
┌─────────────────────────┼──────────────────────────────┐
│                        Rust Domain                      │
│  ┌──────────────────────▼──────────────────────────┐   │
│  │ Rust Native Module                              │   │
│  │ - Pure computation functions                    │   │
│  │ - Stateless design                              │   │
│  │ - Minimal interface                             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Rust Modules Plan for MVP Phase

### 2.1 Required Module

| Module              | Function       | Priority | Status   |
| ------------------- | -------------- | -------- | -------- |
| `ainalyn_tokenizer` | Token counting | P0       | Planning |

### 2.2 Optional Future Modules

| Module           | Function          | Priority |
| ---------------- | ----------------- | -------- |
| `ainalyn_filter` | Content filtering | P1       |
| `ainalyn_crypto` | Crypto/signing    | P2       |

---

## 3. Token Counting Module Design

### 3.1 Rust-side Interface (`rust/src/tokenizer.rs`)

```rust
use pyo3::prelude::*;

/// Token counting result
#[pyclass]
#[derive(Clone)]
pub struct TokenCount {
    #[pyo3(get)]
    pub count: usize,
    #[pyo3(get)]
    pub model: String,
}

/// Count the number of tokens in a piece of text
///
/// # Arguments
/// * `text` - The text to count
/// * `model` - Model name (e.g., "gpt-4", "claude-3")
///
/// # Returns
/// * `TokenCount` - Contains the token count and model used
#[pyfunction]
pub fn count_tokens(text: &str, model: &str) -> PyResult<TokenCount> {
    let encoding = get_encoding_for_model(model)?;
    let count = encoding.encode(text).len();

    Ok(TokenCount {
        count,
        model: model.to_string(),
    })
}

/// Batch count token numbers for multiple texts
#[pyfunction]
pub fn count_tokens_batch(texts: Vec<&str>, model: &str) -> PyResult<Vec<TokenCount>> {
    let encoding = get_encoding_for_model(model)?;

    texts
        .into_iter()
        .map(|text| {
            let count = encoding.encode(text).len();
            Ok(TokenCount {
                count,
                model: model.to_string(),
            })
        })
        .collect()
}

/// Truncate text to a given token count
#[pyfunction]
pub fn truncate_to_tokens(text: &str, max_tokens: usize, model: &str) -> PyResult<String> {
    let encoding = get_encoding_for_model(model)?;
    let tokens = encoding.encode(text);

    if tokens.len() <= max_tokens {
        return Ok(text.to_string());
    }

    let truncated_tokens = &tokens[..max_tokens];
    encoding.decode(truncated_tokens)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))
}

/// Python module definition
#[pymodule]
fn ainalyn_tokenizer(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<TokenCount>()?;
    m.add_function(wrap_pyfunction!(count_tokens, m)?)?;
    m.add_function(wrap_pyfunction!(count_tokens_batch, m)?)?;
    m.add_function(wrap_pyfunction!(truncate_to_tokens, m)?)?;
    Ok(())
}
```

### 3.2 Python Wrapper (`infrastructure/rust/tokenizer.py`)

```python
"""
Python wrapper for the Rust Tokenizer module.

Provides token counting functionality and automatically
falls back to a pure Python implementation when the Rust
module is unavailable.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ainalyn.domain.errors import InternalError

if TYPE_CHECKING:
    from collections.abc import Sequence

# Try to load Rust module
_rust_available = False
_rust_module = None

try:
    import ainalyn_tokenizer as _rust_module
    _rust_available = True
except ImportError:
    pass


@dataclass
class TokenCount:
    """Token counting result"""

    count: int
    model: str


class Tokenizer:
    """
    Token counter.

    Prefers the Rust module and falls back to a Python implementation
    when Rust is not available.
    """

    def __init__(self, model: str = "gpt-4") -> None:
        """
        Initialize Tokenizer.

        Args:
            model: Default model name to use
        """
        self.model = model
        self._use_rust = _rust_available

    @property
    def backend(self) -> str:
        """Currently used backend"""
        return "rust" if self._use_rust else "python"

    def count_tokens(self, text: str, model: str | None = None) -> TokenCount:
        """
        Count the number of tokens in text.

        Args:
            text: The text to count
            model: Model name, uses default if None

        Returns:
            TokenCount containing the result
        """
        target_model = model or self.model

        if self._use_rust and _rust_module:
            result = _rust_module.count_tokens(text, target_model)
            return TokenCount(count=result.count, model=result.model)
        else:
            return self._count_tokens_python(text, target_model)

    def count_tokens_batch(
        self,
        texts: Sequence[str],
        model: str | None = None,
    ) -> list[TokenCount]:
        """
        Batch count token numbers for multiple texts.

        Args:
            texts: List of texts
            model: Model name

        Returns:
            List of TokenCount
        """
        target_model = model or self.model

        if self._use_rust and _rust_module:
            results = _rust_module.count_tokens_batch(list(texts), target_model)
            return [
                TokenCount(count=r.count, model=r.model)
                for r in results
            ]
        else:
            return [
                self._count_tokens_python(text, target_model)
                for text in texts
            ]

    def truncate_to_tokens(
        self,
        text: str,
        max_tokens: int,
        model: str | None = None,
    ) -> str:
        """
        Truncate text to a specified token count.

        Args:
            text: Text to truncate
            max_tokens: Maximum number of tokens
            model: Model name

        Returns:
            Truncated text
        """
        target_model = model or self.model

        if self._use_rust and _rust_module:
            return _rust_module.truncate_to_tokens(text, max_tokens, target_model)
        else:
            return self._truncate_python(text, max_tokens, target_model)

    def _count_tokens_python(self, text: str, model: str) -> TokenCount:
        """Pure Python implementation (fallback)"""
        # Use tiktoken or a simple estimate
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(model)
            count = len(encoding.encode(text))
        except Exception:
            # Last resort: rough estimate
            count = len(text) // 4  # rough estimate

        return TokenCount(count=count, model=model)

    def _truncate_python(self, text: str, max_tokens: int, model: str) -> str:
        """Pure Python truncation implementation"""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(text)
            if len(tokens) <= max_tokens:
                return text
            return encoding.decode(tokens[:max_tokens])
        except Exception:
            # Rough truncation
            estimated_chars = max_tokens * 4
            return text[:estimated_chars]


# Convenience functions
def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Convenience function to count tokens.

    Args:
        text: Text to count
        model: Model name

    Returns:
        Number of tokens
    """
    tokenizer = Tokenizer(model)
    return tokenizer.count_tokens(text).count


def is_rust_available() -> bool:
    """Check whether the Rust module is available"""
    return _rust_available
```

---

## 4. Development Workflow

### 4.1 Rust Module Directory Structure

```
rust/
├── Cargo.toml
├── src/
│   ├── lib.rs              # Module entry
│   ├── tokenizer.rs        # Token counting
│   └── error.rs            # Error definitions
├── tests/
│   └── test_tokenizer.rs   # Rust unit tests
└── benches/
    └── tokenizer_bench.rs  # Performance benchmarks
```

### 4.2 Cargo.toml Configuration

```toml
[package]
name = "ainalyn_tokenizer"
version = "0.1.0"
edition = "2021"

[lib]
name = "ainalyn_tokenizer"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
tiktoken-rs = "0.5"

[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "tokenizer_bench"
harness = false
```

### 4.3 Build Workflow

```bash
# Build for development
cd rust
maturin develop

# Release build (produces wheel)
maturin build --release

# Tests
cargo test
```

### 4.4 CI Integration

```yaml
# .github/workflows/rust.yml

name: Rust Module

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Set up Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install maturin
        run: pip install maturin

      - name: Build wheel
        run: |
          cd rust
          maturin build --release

      - name: Run Rust tests
        run: |
          cd rust
          cargo test

      - name: Upload wheel
        uses: actions/upload-artifact@v4
        with:
          name: wheel-${{ matrix.os }}-${{ matrix.python-version }}
          path: rust/target/wheels/*.whl
```

---

## 5. Error Handling

### 5.1 Rust-side Errors

```rust
// rust/src/error.rs

use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum TokenizerError {
    #[error("Unknown model: {0}")]
    UnknownModel(String),

    #[error("Invalid input: {0}")]
    InvalidInput(String),

    #[error("Encoding error: {0}")]
    EncodingError(String),
}

impl From<TokenizerError> for PyErr {
    fn from(err: TokenizerError) -> PyErr {
        PyValueError::new_err(err.to_string())
    }
}
```

### 5.2 Python-side Error Translation

```python
# infrastructure/rust/tokenizer.py

from ainalyn.domain.errors import InternalError, ValidationError

def _handle_rust_error(error: Exception) -> None:
    """Translate Rust errors into SDK errors"""
    error_msg = str(error)

    if "Unknown model" in error_msg:
        raise ValidationError(
            message=error_msg,
            code="DOM_VAL_INVALID_MODEL",
            field="model",
        )
    elif "Invalid input" in error_msg:
        raise ValidationError(
            message=error_msg,
            code="DOM_VAL_INVALID_INPUT",
        )
    else:
        raise InternalError(
            message=f"Tokenizer error: {error_msg}",
            code="INT_ERR_TOKENIZER",
        )
```

---

## 6. Performance Testing

### 6.1 Rust Benchmarks

```rust
// rust/benches/tokenizer_bench.rs

use criterion::{black_box, criterion_group, criterion_main, Criterion};
use ainalyn_tokenizer::count_tokens;

fn benchmark_count_tokens(c: &mut Criterion) {
    let short_text = "Hello, world!";
    let medium_text = "Lorem ipsum ".repeat(100);
    let long_text = "Lorem ipsum ".repeat(1000);

    c.bench_function("count_tokens_short", |b| {
        b.iter(|| count_tokens(black_box(short_text), "gpt-4"))
    });

    c.bench_function("count_tokens_medium", |b| {
        b.iter(|| count_tokens(black_box(&medium_text), "gpt-4"))
    });

    c.bench_function("count_tokens_long", |b| {
        b.iter(|| count_tokens(black_box(&long_text), "gpt-4"))
    });
}

criterion_group!(benches, benchmark_count_tokens);
criterion_main!(benches);
```

### 6.2 Python-side Performance Comparison Tests

```python
# tests/performance/test_tokenizer_performance.py

import pytest
import time
from ainalyn.infrastructure.rust.tokenizer import Tokenizer, is_rust_available

@pytest.mark.slow
class TestTokenizerPerformance:
    """Tokenizer performance tests"""

    @pytest.fixture
    def sample_texts(self) -> list[str]:
        return [
            "Short text",
            "Medium text " * 100,
            "Long text " * 1000,
        ]

    def test_rust_vs_python_performance(self, sample_texts: list[str]):
        """Compare Rust and Python performance"""
        if not is_rust_available():
            pytest.skip("Rust module not available")

        rust_tokenizer = Tokenizer()
        rust_tokenizer._use_rust = True

        python_tokenizer = Tokenizer()
        python_tokenizer._use_rust = False

        for text in sample_texts:
            # Time Rust
            start = time.perf_counter()
            for _ in range(100):
                rust_tokenizer.count_tokens(text)
            rust_time = time.perf_counter() - start

            # Time Python
            start = time.perf_counter()
            for _ in range(100):
                python_tokenizer.count_tokens(text)
            python_time = time.perf_counter() - start

            # Rust should be faster
            assert rust_time < python_time, (
                f"Rust ({rust_time:.4f}s) should be faster than "
                f"Python ({python_time:.4f}s) for text length {len(text)}"
            )

    def test_batch_performance(self, sample_texts: list[str]):
        """Batch processing performance"""
        if not is_rust_available():
            pytest.skip("Rust module not available")

        tokenizer = Tokenizer()
        batch = sample_texts * 100

        start = time.perf_counter()
        results = tokenizer.count_tokens_batch(batch)
        elapsed = time.perf_counter() - start

        assert len(results) == len(batch)
        # Batch processing should complete within a reasonable time
        assert elapsed < 1.0, f"Batch processing took too long: {elapsed:.2f}s"
```

---

## 7. Fallback Strategy

### 7.1 Fallback Scenarios

| Scenario                  | Behavior                                 |
| ------------------------- | ---------------------------------------- |
| Rust module not installed | Automatically use Python implementation  |
| Rust module fails to load | Log a warning, use Python implementation |
| Rust function errors      | Translate into SDK errors, no fallback   |

### 7.2 Fallback Notification

```python
# infrastructure/rust/__init__.py

import logging
from .tokenizer import is_rust_available

logger = logging.getLogger("ainalyn.rust")

def check_rust_modules() -> dict[str, bool]:
    """Check Rust module status"""
    status = {
        "tokenizer": is_rust_available(),
    }

    for module, available in status.items():
        if not available:
            logger.warning(
                f"Rust module '{module}' not available, "
                "using Python fallback (may be slower)"
            )

    return status
```

---

## 8. Development Checklist

### Adding a New Rust Module

* [ ] Confirm the functionality truly needs Rust (performance-critical)
* [ ] Design a minimal interface (pure functions, stateless)
* [ ] Implement the Rust module and tests
* [ ] Implement the Python wrapper and fallback behavior
* [ ] Add performance comparison tests
* [ ] Update CI build pipeline
* [ ] Document the interface and usage

### Maintaining Rust Modules

* [ ] Keep the Rust toolchain up to date
* [ ] Run performance tests regularly
* [ ] Ensure cross-platform builds work correctly
* [ ] Keep Python fallback implementations in sync

---

*Last Updated: 2024-12*
