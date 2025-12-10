# Commit Guidelines and Best Practices

> This document defines the commit conventions for the open-source project to ensure that the Git history is clear, traceable, and professional.

## 1. Commit Message Format

### 1.1 Standard Format

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Explanation of each part:**

| Part      | Required    | Description                         |
| --------- | ----------- | ----------------------------------- |
| `type`    | Yes         | Type of change                      |
| `scope`   | Recommended | Area of impact                      |
| `subject` | Yes         | Short description (≤ 50 characters) |
| `body`    | Optional    | Detailed explanation                |
| `footer`  | Optional    | Related issues, breaking changes    |

### 1.2 Type Definitions

| Type       | Description                      | Emoji | Example                                |
| ---------- | -------------------------------- | ----- | -------------------------------------- |
| `feat`     | New feature                      | ✨     | `feat(chat): add streaming support`    |
| `fix`      | Bug fix                          | 🐛    | `fix(storage): prevent memory leak`    |
| `docs`     | Documentation                    | 📝    | `docs(api): update usage examples`     |
| `style`    | Formatting (no logic change)     | 💄    | `style: apply black formatting`        |
| `refactor` | Refactoring (no behavior change) | ♻️    | `refactor(middleware): simplify chain` |
| `perf`     | Performance improvement          | ⚡️    | `perf(tokenizer): use rust module`     |
| `test`     | Test-related                     | ✅     | `test(provider): add retry tests`      |
| `build`    | Build system                     | 📦    | `build: update dependencies`           |
| `ci`       | CI configuration                 | 👷    | `ci: add coverage reporting`           |
| `chore`    | Misc (no src/test impact)        | 🔧    | `chore: update .gitignore`             |
| `revert`   | Revert changes                   | ⏪     | `revert: revert feat(chat)...`         |

### 1.3 Scope Definitions

**By architecture layer:**

| Scope       | Description                                       |
| ----------- | ------------------------------------------------- |
| `domain`    | Domain layer (models, ports, errors)              |
| `app`       | Application layer (clients, middleware, usecases) |
| `infra`     | Infrastructure layer (providers, storage, rust)   |
| `interface` | Interface layer (public API, types)               |

**By feature module:**

| Scope          | Description             |
| -------------- | ----------------------- |
| `chat`         | Chat service            |
| `translation`  | Translation service     |
| `image`        | Image-related services  |
| `speech`       | Speech-related services |
| `video`        | Video-related services  |
| `music`        | Music generation        |
| `travel`       | Travel planning         |
| `presentation` | Presentation generation |
| `history`      | History service         |
| `settings`     | Settings management     |

**By technical component:**

| Scope        | Description               |
| ------------ | ------------------------- |
| `provider`   | Provider implementation   |
| `storage`    | Storage implementation    |
| `middleware` | Middleware implementation |
| `events`     | Event system              |
| `errors`     | Error handling            |
| `logging`    | Logging system            |
| `types`      | Type definitions          |
| `rust`       | Rust modules              |
| `deps`       | Dependency management     |

---

## 2. Subject Writing Rules

### 2.1 Basic Rules

1. **Use the imperative mood**

   * ✅ `add support for streaming`
   * ❌ `added support for streaming`
   * ❌ `adds support for streaming`

2. **Start with a lowercase letter**

   * ✅ `add user authentication`
   * ❌ `Add user authentication`

3. **No trailing period**

   * ✅ `fix memory leak in storage`
   * ❌ `fix memory leak in storage.`

4. **Limit length to 50 characters**

   * Ensures full display on GitHub
   * Enforces concise expression

### 2.2 Common Verbs

| Action       | Verbs                             | Example                            |
| ------------ | --------------------------------- | ---------------------------------- |
| Add features | add, implement, introduce         | `add retry middleware`             |
| Remove       | remove, delete, drop              | `remove deprecated API`            |
| Fix          | fix, resolve, correct             | `fix null pointer exception`       |
| Update       | update, upgrade, bump             | `update httpx to 0.25`             |
| Improve      | improve, enhance, optimize        | `improve error messages`           |
| Refactor     | refactor, restructure, reorganize | `refactor client initialization`   |
| Rename       | rename, move                      | `rename ChatService to ChatClient` |
| Simplify     | simplify, streamline              | `simplify middleware chain`        |
| Extract      | extract, separate                 | `extract common validation logic`  |
| Merge        | merge, combine, consolidate       | `merge duplicate handlers`         |

### 2.3 Subject Examples

**Good** ✅

```text
feat(chat): add multi-provider support
fix(storage): prevent session data corruption
refactor(middleware): extract retry logic to utility
perf(tokenizer): switch to rust implementation
docs(api): add streaming usage examples
test(provider): add unit tests for error handling
```

**Bad** ❌

```text
feat(chat): Added streaming          # past tense
fix: bug fix                         # not specific
update code                          # no scope, not specific
refactor(middleware): Refactoring    # capitalized, noun form
WIP                                  # meaningless
misc changes                         # not specific
```

---

## 3. Body Writing Rules

### 3.1 When a Body Is Needed

* The change is non-obvious and needs a “why”
* There are multiple related changes to list
* Important implementation details should be recorded
* There is a breaking change that needs explanation

### 3.2 Body Format

```text
<type>(<scope>): <subject>

<blank line>
<body paragraph 1: explain WHY this change is made>

<body paragraph 2: explain HOW it is implemented (if needed)>

<body paragraph 3: list key changes (if needed)>
```

### 3.3 Body Example

```text
feat(chat): add automatic failover between providers

When the primary provider fails, the client now automatically
attempts to use secondary providers before returning an error.
This improves reliability for production applications.

Implementation details:
- Add ProviderChain class to manage provider ordering
- Implement health check mechanism for each provider
- Add configurable retry delays between providers

Changes:
- ChatClient constructor now accepts provider list
- Add new FailoverConfig options
- Update documentation with failover examples
```

---

## 4. Footer Rules

### 4.1 Related Issues

```text
Closes #123
Fixes #456
Resolves #789
```

**Multiple issues:**

```text
Closes #123, #456
Fixes #789
```

### 4.2 Breaking Changes

Use the `BREAKING CHANGE:` marker (note the colon):

```text
feat(api)!: change response format for chat endpoint

BREAKING CHANGE: ChatResponse.message is now ChatResponse.content.
Users need to update their code to use the new field name.

Migration:
- Before: response.message
- After: response.content
```

Or add `!` after the type:

```text
feat(api)!: rename ChatResponse fields
```

### 4.3 Co-authors

```text
Co-authored-by: Name <email@example.com>
Co-authored-by: Another Name <another@example.com>
```

---

## 5. Complete Examples

### 5.1 Simple Change

```text
fix(storage): prevent duplicate session IDs

Closes #234
```

### 5.2 New Feature

```text
feat(translation): add batch translation support

Add ability to translate multiple texts in a single API call,
reducing latency for applications that need to translate
multiple strings.

New methods:
- TranslationClient.translate_batch()
- TranslationClient.translate_batch_async()

The batch size is limited to 100 items per request to prevent
timeout issues.

Closes #156
```

### 5.3 Refactor

```text
refactor(middleware): consolidate retry logic

Extract common retry logic from RetryMiddleware and
RateLimitMiddleware into a shared RetryExecutor utility.

This reduces code duplication and ensures consistent retry
behavior across all middleware that needs it.

Changes:
- Add RetryExecutor in infrastructure/utils/retry.py
- Update RetryMiddleware to use RetryExecutor
- Update RateLimitMiddleware to use RetryExecutor
- Add unit tests for RetryExecutor
```

### 5.4 Breaking Change

```text
feat(chat)!: restructure ChatResponse for consistency

BREAKING CHANGE: ChatResponse structure has changed.

Before:
  response.message.text
  response.message.role

After:
  response.content
  response.role

Migration guide:
1. Update all response.message.text to response.content
2. Update all response.message.role to response.role
3. Remove any direct access to response.message

Closes #312
```

### 5.5 Performance Improvement

```text
perf(tokenizer): implement rust-based token counting

Replace pure Python token counting with Rust implementation
using tiktoken-rs. Benchmarks show 10-50x improvement:

| Text Size | Python | Rust   | Speedup |
|-----------|--------|--------|---------|
| 100 chars | 2.1ms  | 0.1ms  | 21x     |
| 1K chars  | 18ms   | 0.4ms  | 45x     |
| 10K chars | 180ms  | 3.5ms  | 51x     |

Falls back to Python implementation if Rust module
is not available.
```

---

## 6. Commit Strategy

### 6.1 Atomic Commits

Each commit should be **atomic**:

* One commit does exactly one logical thing
* It can be understood on its own
* It can be reverted independently

**Good** ✅

```text
commit 1: feat(chat): add Provider interface
commit 2: feat(chat): implement OpenAI provider
commit 3: feat(chat): implement Claude provider
commit 4: test(chat): add provider unit tests
```

**Bad** ❌

```text
commit 1: add chat feature with multiple providers and tests
```

### 6.2 What Should Not Be Committed

* ❌ Build artifacts (`__pycache__/`, `*.pyc`)
* ❌ IDE settings (`.idea/`, `.vscode/`, unless shared on purpose)
* ❌ System files (`.DS_Store`, `Thumbs.db`)
* ❌ Sensitive information (API keys, passwords)
* ❌ Large binary files
* ❌ `node_modules`, `.venv`

### 6.3 Checks Before Committing

```bash
# 1. Check staged changes
git diff --staged

# 2. Ensure no sensitive information
git diff --staged | grep -i "api_key\|password\|secret"

# 3. Run tests
pytest tests/unit -v

# 4. Run linters
ruff check src tests
mypy src
```

---

## 7. Git Hooks Configuration

### 7.1 Pre-commit Hook

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: commit-msg-check
        name: Commit Message Check
        entry: python scripts/check_commit_msg.py
        language: python
        stages: [commit-msg]
```

### 7.2 Commit Message Check Script

```python
#!/usr/bin/env python3
"""scripts/check_commit_msg.py - Validate commit message format."""

import re
import sys
from pathlib import Path

TYPES = [
    "feat", "fix", "docs", "style", "refactor",
    "perf", "test", "build", "ci", "chore", "revert"
]

SCOPES = [
    # Architecture layers
    "domain", "app", "infra", "interface",
    # Feature modules
    "chat", "translation", "image", "speech", "video",
    "music", "travel", "presentation", "history", "settings",
    # Technical components
    "provider", "storage", "middleware", "events", "errors",
    "logging", "types", "rust", "deps",
]

# Pattern: type(scope)!: subject
PATTERN = re.compile(
    r"^(?P<type>" + "|".join(TYPES) + r")"
    r"(?:\((?P<scope>" + "|".join(SCOPES) + r")\))?"
    r"(?P<breaking>!)?"
    r": (?P<subject>.+)$"
)


def validate_commit_message(message: str) -> tuple[bool, str]:
    """Validate commit message format."""
    lines = message.strip().split("\n")

    if not lines:
        return False, "Empty commit message"

    first_line = lines[0]

    # Check first line format
    match = PATTERN.match(first_line)
    if not match:
        return False, (
            f"Invalid format: {first_line}\n"
            f"Expected: <type>(<scope>): <subject>\n"
            f"Types: {', '.join(TYPES)}\n"
            f"Scopes: {', '.join(SCOPES)}"
        )

    subject = match.group("subject")

    # Check subject length
    if len(first_line) > 72:
        return False, f"First line too long ({len(first_line)} > 72 chars)"

    # Check subject starts with lowercase
    if subject[0].isupper():
        return False, "Subject should start with lowercase"

    # Check subject doesn't end with period
    if subject.endswith("."):
        return False, "Subject should not end with period"

    # Check blank line after subject (if body exists)
    if len(lines) > 1 and lines[1].strip():
        return False, "Second line should be blank"

    return True, "OK"


def main() -> int:
    """Main entry point."""
    commit_msg_file = sys.argv[1] if len(sys.argv) > 1 else ".git/COMMIT_EDITMSG"

    try:
        message = Path(commit_msg_file).read_text()
    except FileNotFoundError:
        print(f"Error: {commit_msg_file} not found")
        return 1

    # Skip merge commits
    if message.startswith("Merge"):
        return 0

    valid, error = validate_commit_message(message)

    if not valid:
        print(f"❌ Commit message validation failed:\n{error}")
        return 1

    print("✅ Commit message is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 8. Branch and Commit Strategy

### 8.1 Feature Branch Strategy

```text
main ──●──────────────────●──────────▶
        \                /
develop ─●───●───●───●───●───●───────▶
          \         /
feature/x  ●───●───●
```

### 8.2 Commit Cleanup (Squash/Rebase)

**Clean up commits before opening a PR:**

```bash
# Interactive rebase to clean up the last 5 commits
git rebase -i HEAD~5

# Choose actions in the editor:
# pick   - keep
# squash - merge into previous
# fixup  - merge but discard message
# reword - edit message
```

**Merge strategy:**

* WIP commits → squash into one meaningful commit
* Small related tweaks → squash into one
* Independent features → keep separate

### 8.3 Example: Before / After Cleanup

**Before:**

```text
wip
fix typo
add tests
more fixes
done
```

**After:**

```text
feat(chat): add streaming response support

Implement server-sent events for real-time streaming responses.
Add StreamingMiddleware and update ChatClient to support
async iteration.

Closes #123
```

---

## 9. Commit Checklist

### Before Each Commit

* [ ] The change is a single logical unit
* [ ] All tests pass
* [ ] No linter warnings
* [ ] No sensitive information
* [ ] Commit message follows the format
* [ ] Subject clearly describes the change
* [ ] Body explains “why” when needed
* [ ] Related issues are referenced (if any)
* [ ] Breaking changes are marked

### Before a PR

* [ ] Commits have been cleaned up (no WIP/fixup noise)
* [ ] Each commit can be understood independently
* [ ] The commit history tells a clear story
* [ ] No unnecessary merge commits

---

## 10. Recommended Tools

### 10.1 Commit Helper Tools

| Tool                                               | Purpose                               |
| -------------------------------------------------- | ------------------------------------- |
| [commitizen](https://github.com/commitizen/cz-cli) | Interactive commit message generation |
| [commitlint](https://commitlint.js.org/)           | Commit message validation             |
| [pre-commit](https://pre-commit.com/)              | Git hooks management                  |

### 10.2 Suggested Git Settings

```bash
# Set default editor
git config --global core.editor "code --wait"

# Set commit template
git config --global commit.template ~/.gitmessage

# Configure line endings
git config --global core.autocrlf input  # macOS/Linux
git config --global core.autocrlf true   # Windows
```

### 10.3 Commit Template

```bash
# ~/.gitmessage

# <type>(<scope>): <subject>
#
# <body>
#
# <footer>
#
# --- COMMIT RULES ---
# Type: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert
# Scope: domain|app|infra|interface|chat|translation|...
# Subject: lowercase, imperative, no period, ≤50 chars
# Body: explain WHY, not WHAT (wrap at 72 chars)
# Footer: Closes #issue, BREAKING CHANGE:
```

---

*Last Updated: 2024-12*
