# =============================================================================
# Ainalyn SDK - Makefile
# =============================================================================
# Common development commands for the SDK project.
# Run `make help` to see all available commands.
# =============================================================================

.DEFAULT_GOAL := help
SHELL := /bin/bash

# Project settings
PACKAGE_NAME := ainalyn
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Python settings
PYTHON := python
PIP := pip
PYTEST := pytest
COVERAGE := coverage

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# =============================================================================
# Help
# =============================================================================

.PHONY: help
help: ## Show this help message
	@echo -e "$(BLUE)Ainalyn SDK - Development Commands$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================

.PHONY: install
install: ## Install package in development mode
	$(PIP) install -e ".[dev]"

.PHONY: install-test
install-test: ## Install test dependencies only
	$(PIP) install -e ".[test]"

.PHONY: install-lint
install-lint: ## Install lint dependencies only
	$(PIP) install -e ".[lint]"

.PHONY: install-type
install-type: ## Install type checking dependencies only
	$(PIP) install -e ".[type]"

.PHONY: install-docs
install-docs: ## Install documentation dependencies
	$(PIP) install -e ".[docs]"

.PHONY: install-all
install-all: ## Install all optional dependencies
	$(PIP) install -e ".[all]"

.PHONY: install-hooks
install-hooks: ## Install pre-commit hooks
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo -e "$(GREEN)Pre-commit hooks installed$(NC)"

# =============================================================================
# Development Setup
# =============================================================================

.PHONY: setup
setup: install install-hooks ## Full development setup
	@echo -e "$(GREEN)Development environment ready!$(NC)"

.PHONY: venv
venv: ## Create virtual environment
	$(PYTHON) -m venv .venv
	@echo -e "$(GREEN)Virtual environment created. Activate with:$(NC)"
	@echo "  source .venv/bin/activate  # Linux/macOS"
	@echo "  .venv\\Scripts\\activate    # Windows"

# =============================================================================
# Code Quality
# =============================================================================

.PHONY: lint
lint: ## Run all linters
	@echo -e "$(BLUE)Running Ruff...$(NC)"
	ruff check $(SRC_DIR) $(TEST_DIR)
	@echo -e "$(BLUE)Running Ruff format check...$(NC)"
	ruff format --check $(SRC_DIR) $(TEST_DIR)
	@echo -e "$(GREEN)All lint checks passed!$(NC)"

.PHONY: lint-fix
lint-fix: ## Run linters and fix issues
	@echo -e "$(BLUE)Running Ruff with fixes...$(NC)"
	ruff check --fix $(SRC_DIR) $(TEST_DIR)
	@echo -e "$(BLUE)Running Ruff format...$(NC)"
	ruff format $(SRC_DIR) $(TEST_DIR)
	@echo -e "$(GREEN)Lint fixes applied!$(NC)"

.PHONY: format
format: ## Format code with Ruff/Black
	ruff format $(SRC_DIR) $(TEST_DIR)
	@echo -e "$(GREEN)Code formatted!$(NC)"

.PHONY: type
type: ## Run type checking with mypy
	@echo -e "$(BLUE)Running MyPy...$(NC)"
	mypy $(SRC_DIR)
	@echo -e "$(GREEN)Type checking passed!$(NC)"

.PHONY: check
check: lint type ## Run all code quality checks
	@echo -e "$(GREEN)All checks passed!$(NC)"

# =============================================================================
# Testing
# =============================================================================

.PHONY: test
test: ## Run unit tests
	$(PYTEST) $(TEST_DIR)/unit -v

.PHONY: test-fast
test-fast: ## Run unit tests (quick mode, no verbose)
	$(PYTEST) $(TEST_DIR)/unit -q

.PHONY: test-unit
test-unit: ## Run unit tests
	$(PYTEST) $(TEST_DIR)/unit -v

.PHONY: test-integration
test-integration: ## Run integration tests
	$(PYTEST) $(TEST_DIR)/integration -v

.PHONY: test-contract
test-contract: ## Run contract tests
	$(PYTEST) $(TEST_DIR)/contract -v

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests
	$(PYTEST) $(TEST_DIR)/e2e -v

.PHONY: test-all
test-all: ## Run all tests
	$(PYTEST) $(TEST_DIR) -v

.PHONY: test-slow
test-slow: ## Run slow tests (marked with @pytest.mark.slow)
	$(PYTEST) $(TEST_DIR) -v -m slow

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	$(PYTEST) $(TEST_DIR)/unit --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo -e "$(GREEN)Coverage report generated in htmlcov/$(NC)"

.PHONY: test-cov-report
test-cov-report: ## Open coverage report in browser
	@$(PYTHON) -m webbrowser htmlcov/index.html

# =============================================================================
# Security
# =============================================================================

.PHONY: security
security: ## Run security checks
	@echo -e "$(BLUE)Running Bandit...$(NC)"
	bandit -r $(SRC_DIR) -c pyproject.toml
	@echo -e "$(GREEN)Security check passed!$(NC)"

.PHONY: audit
audit: ## Audit dependencies for security vulnerabilities
	@echo -e "$(BLUE)Running pip-audit...$(NC)"
	pip-audit || true
	@echo -e "$(BLUE)Running safety...$(NC)"
	safety check || true

# =============================================================================
# Build
# =============================================================================

.PHONY: build
build: clean ## Build distribution packages
	@echo -e "$(BLUE)Building package...$(NC)"
	$(PYTHON) -m build
	@echo -e "$(GREEN)Build complete! Packages in dist/$(NC)"

.PHONY: build-check
build-check: build ## Build and check packages
	twine check dist/*
	@echo -e "$(GREEN)Package check passed!$(NC)"

# =============================================================================
# Documentation
# =============================================================================

.PHONY: docs
docs: ## Build documentation
	mkdocs build
	@echo -e "$(GREEN)Documentation built in site/$(NC)"

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	mkdocs serve

# =============================================================================
# Cleanup
# =============================================================================

.PHONY: clean
clean: ## Remove build artifacts
	@echo -e "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(SRC_DIR)/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo -e "$(GREEN)Clean complete!$(NC)"

.PHONY: clean-test
clean-test: ## Remove test artifacts
	@echo -e "$(BLUE)Cleaning test artifacts...$(NC)"
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .hypothesis/
	@echo -e "$(GREEN)Test artifacts cleaned!$(NC)"

.PHONY: clean-lint
clean-lint: ## Remove lint cache
	@echo -e "$(BLUE)Cleaning lint cache...$(NC)"
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	@echo -e "$(GREEN)Lint cache cleaned!$(NC)"

.PHONY: clean-all
clean-all: clean clean-test clean-lint ## Remove all artifacts
	@echo -e "$(GREEN)All artifacts cleaned!$(NC)"

# =============================================================================
# Pre-commit
# =============================================================================

.PHONY: pre-commit
pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

.PHONY: pre-commit-update
pre-commit-update: ## Update pre-commit hooks
	pre-commit autoupdate

# =============================================================================
# Rust (if applicable)
# =============================================================================

.PHONY: rust-build
rust-build: ## Build Rust modules
	cd rust && maturin develop

.PHONY: rust-build-release
rust-build-release: ## Build Rust modules (release)
	cd rust && maturin build --release

.PHONY: rust-test
rust-test: ## Run Rust tests
	cd rust && cargo test

.PHONY: rust-bench
rust-bench: ## Run Rust benchmarks
	cd rust && cargo bench

# =============================================================================
# Git Helpers
# =============================================================================

.PHONY: commit-check
commit-check: check test ## Run all checks before commit
	@echo -e "$(GREEN)Ready to commit!$(NC)"

# =============================================================================
# CI Simulation
# =============================================================================

.PHONY: ci
ci: check test-all security ## Simulate CI pipeline locally
	@echo -e "$(GREEN)CI simulation complete!$(NC)"

# =============================================================================
# Version
# =============================================================================

.PHONY: version
version: ## Show current version
	@$(PYTHON) -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"
