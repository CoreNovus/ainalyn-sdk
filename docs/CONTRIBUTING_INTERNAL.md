# Internal Contribution Guide

> This document describes the internal development workflow, branch strategy, and PR guidelines for the SDK.
>
> **Important**: This is an open-source project, and the entire commit history is public. Please ensure every commit is professional, clear, and meaningful. For detailed commit conventions, see [COMMIT_CONVENTIONS.md](./COMMIT_CONVENTIONS.md).

## 1. Development Environment Setup

### 1.1 Required Tools

| Tool     | Minimum Version | Purpose                   |
| -------- | --------------- | ------------------------- |
| Python   | 3.11            | Primary language          |
| uv / pip | Latest          | Package management        |
| Rust     | 1.70+           | Native modules (optional) |
| Git      | 2.30+           | Version control           |

### 1.2 Setup Steps

```bash
# 1. Clone the repo
git clone <repo-url>
cd ainalyn_sdk

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install development dependencies
pip install -e ".[dev]"

# 4. Install pre-commit hooks
pre-commit install

# 5. Verify setup
pytest tests/unit -v
```

### 1.3 IDE Settings

**Recommended VSCode settings** (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "strict",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

---

## 2. Branch Strategy

### 2.1 Branch Types

| Branch Type  | Naming Format                | Purpose                            | From      |
| ------------ | ---------------------------- | ---------------------------------- | --------- |
| `main`       | -                            | Stable releases                    | -         |
| `develop`    | -                            | Integration branch for development | -         |
| `feature/*`  | `feature/add-video-analysis` | New features                       | `develop` |
| `fix/*`      | `fix/chat-session-leak`      | Bug fixes                          | `develop` |
| `refactor/*` | `refactor/middleware-chain`  | Refactoring                        | `develop` |
| `docs/*`     | `docs/api-reference`         | Documentation                      | `develop` |
| `release/*`  | `release/v0.1.0`             | Release prep                       | `develop` |
| `hotfix/*`   | `hotfix/critical-auth-fix`   | Urgent fixes                       | `main`    |

### 2.2 Branch Flow

```
main ─────●─────────────●─────────────●──────────▶
           \           /             /
            \         /             /
develop ─────●───●───●───●───●───●───●───●──────▶
              \     /   \     /
               \   /     \   /
feature/xxx ────●─●       ●─●
                        fix/yyy
```

### 2.3 Branch Naming Examples

```bash
# New features
feature/add-translation-api
feature/implement-streaming-response
feature/speech-to-text-client

# Bug fixes
fix/memory-leak-in-storage
fix/retry-middleware-infinite-loop
fix/incorrect-token-counting

# Refactors
refactor/split-large-client
refactor/improve-error-hierarchy

# Docs
docs/add-api-examples
docs/update-architecture-guide
```

---

## 3. Commit Conventions

> **Full conventions**: Refer to [COMMIT_CONVENTIONS.md](./COMMIT_CONVENTIONS.md) for complete commit writing guidelines.

### 3.1 Core Principles

As an open-source project, our commit history is public and must follow these principles:

1. **Atomicity**: Each commit should do exactly one thing and be independently understandable and revertible.
2. **Clarity**: The commit message clearly explains “what” was done and “why”.
3. **Professionalism**: No meaningless commits such as WIP or typo fix only (commits must be cleaned up before PR).
4. **Traceability**: Relate to relevant issues and mark breaking changes.

### 3.2 Commit Message Format

```text
<type>(<scope>): <subject>

<body>

<footer>
```

| Part      | Required    | Rules                                                          |
| --------- | ----------- | -------------------------------------------------------------- |
| `type`    | Yes         | feat, fix, docs, style, refactor, perf, test, build, ci, chore |
| `scope`   | Recommended | domain, app, infra, chat, translation, provider, storage...    |
| `subject` | Yes         | Imperative, starts with lowercase, no period, ≤ 50 characters  |
| `body`    | Optional    | Explain “why”, each line ≤ 72 characters                       |
| `footer`  | Optional    | Closes #issue, BREAKING CHANGE:                                |

### 3.3 Good vs Bad Examples

**Good** ✅

```bash
feat(chat): add automatic provider failover

When primary provider fails, automatically attempt secondary
providers before returning error. Improves reliability for
production applications.

- Add ProviderChain class for provider management
- Implement health check mechanism
- Add configurable retry delays

Closes #123
```

**Bad** ❌

```bash
wip                           # meaningless
fix bug                       # not specific
Update chat.py                # does not say what changed
Added new feature             # past tense, not specific
```

### 3.4 Commits Must Be Cleaned Up Before PR

```bash
# Interactive rebase to clean up commits
git rebase -i HEAD~5

# Squash WIP commits into meaningful commits
# pick   → keep
# squash → merge into previous
# fixup  → merge but discard message
# reword → edit message
```

**Before cleanup**:

```text
wip
fix typo
add tests
more fixes
done
```

**After cleanup**:

```text
feat(chat): add streaming response support

Implement SSE for real-time streaming. Add StreamingMiddleware
and update ChatClient for async iteration.

Closes #123
```

### 3.5 Prohibited

* ❌ Committing sensitive information (API keys, passwords)
* ❌ Committing build artifacts (`__pycache__/`, `*.pyc`)
* ❌ Committing IDE settings (unless intentionally shared for the team)
* ❌ Keeping WIP/fixup commits in PRs
* ❌ Single commits with more than 500 lines of changes

---

## 4. Pull Request Workflow

### 4.1 Checklist Before Creating a PR

* [ ] Code passes all linter checks
* [ ] All tests pass
* [ ] New features have corresponding tests
* [ ] Related documentation is updated
* [ ] Commit messages follow conventions
* [ ] No unnecessary console.log / print
* [ ] No hard-coded sensitive information

### 4.2 PR Template

```markdown
## Overview
<!-- Briefly describe what this PR does -->

## Type of Change
- [ ] New feature (feature)
- [ ] Bug fix (fix)
- [ ] Refactor (refactor)
- [ ] Documentation (docs)
- [ ] Tests (test)
- [ ] Other

## Changes
<!-- Describe the changes in detail -->

## Test Plan
<!-- Explain how these changes were tested -->

## Related Issues
<!-- Related issues, e.g. Closes #123 -->

## Checklist
- [ ] Code follows project conventions
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Local tests passed

## Screenshots (if applicable)
<!-- Add relevant screenshots -->
```

### 4.3 PR Size Guidelines

| Size | Lines Changed | Recommendation     |
| ---- | ------------- | ------------------ |
| XS   | < 50          | Quick merge        |
| S    | 50–200        | Normal review      |
| M    | 200–500       | Thorough review    |
| L    | 500–1000      | Consider splitting |
| XL   | > 1000        | Must be split      |

### 4.4 Code Review Focus

**Reviewers should check:**

1. **Architectural correctness**

   * Is the code placed in the correct layer?
   * Are dependencies in the correct direction?
   * Does it respect abstraction boundaries?

2. **Code quality**

   * Are names clear?
   * Is the logic sound?
   * Is duplicate code avoided?

3. **Test coverage**

   * Are there sufficient tests?
   * Do tests cover edge cases?

4. **Documentation updates**

   * Are API changes documented?
   * Is complex logic commented where needed?

---

## 5. Local Development Workflow

### 5.1 Daily Development Flow

```bash
# 1. Ensure develop is up to date
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Develop and test
# ... edit code ...
pytest tests/unit -v  # run tests

# 4. Commit changes
git add .
git commit -m "feat(scope): description"

# 5. Push branch
git push origin feature/my-feature

# 6. Create PR
# Open a PR on GitHub/GitLab
```

### 5.2 Test Commands

```bash
# Run all unit tests
pytest tests/unit -v

# Run a specific test file
pytest tests/unit/application/clients/test_chat_client.py -v

# Run a specific test
pytest tests/unit -k "test_send_message" -v

# Run integration tests
pytest tests/integration -v

# Run tests with coverage report
pytest tests/unit --cov=src --cov-report=html

# Run type checks
mypy src

# Run linter
ruff check src tests
black --check src tests
```

### 5.3 Common Make Targets

```makefile
# Makefile

.PHONY: install test test-all lint format clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/unit -v

test-all:
	pytest tests -v

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist
	find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## 6. CI/CD Workflow

### 6.1 PR Checks

Each PR automatically runs:

1. **Lint Check**

   * ruff
   * black --check
   * mypy

2. **Unit Tests**

   * pytest tests/unit
   * Coverage check (≥ 85%)

3. **Integration Tests**

   * pytest tests/integration

4. **Contract Tests**

   * pytest tests/contract

5. **Build Check**

   * pip install -e .
   * Ensure installation works

### 6.2 Post-Merge Workflow

After merging into `develop`:

1. Run the full test suite
2. Update coverage reports
3. Build documentation (if changed)

### 6.3 Release Workflow

1. Create `release/vX.Y.Z` from `develop`
2. Update version and CHANGELOG
3. Run full tests
4. Merge into `main` and tag
5. Automatically publish to PyPI

---

## 7. Troubleshooting

### 7.1 Common Issues

**Q: Tests fail on CI but pass locally**

```bash
# Ensure dependencies are consistent
pip install -e ".[dev]" --force-reinstall

# Clear caches
rm -rf .pytest_cache .mypy_cache
```

**Q: Pre-commit fails**

```bash
# Run formatters manually
black src tests
ruff check --fix src tests
```

**Q: Type checking errors**

```bash
# Show detailed errors
mypy src --show-error-codes
```

### 7.2 Contact

* **Technical issues**: Open an Issue or Discussion
* **Urgent problems**: Contact project maintainers
* **Security issues**: Contact privately, do not discuss publicly

---

## 8. Release Checklist

### Before Release

* [ ] All tests pass
* [ ] Documentation is updated
* [ ] CHANGELOG is updated
* [ ] Version number is updated
* [ ] Breaking changes are recorded
* [ ] Tested in staging environment

### After Release

* [ ] PyPI release successful
* [ ] Documentation site updated
* [ ] GitHub Release created
* [ ] Related issues closed

---

*Last Updated: 2024-12*
