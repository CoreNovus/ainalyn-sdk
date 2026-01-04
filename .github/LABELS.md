# Issue Labels Strategy

This document defines the labeling strategy for issues and pull requests in the Ainalyn SDK repository.

## Why Labels Matter

Labels help:

- **New contributors** find suitable issues (`good first issue`, `help wanted`)
- **Maintainers** prioritize and organize work
- **Community** understand project status and focus areas
- **Platforms** like [goodfirstissue.dev](https://goodfirstissue.dev/) discover our project

## Label Categories

### Type Labels (What kind of issue is this?)

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | #d73a4a | Something isn't working |
| `enhancement` | #a2eeef | New feature or request |
| `documentation` | #0075ca | Improvements or additions to documentation |
| `refactor` | #fbca04 | Code refactoring without changing functionality |
| `test` | #0e8a16 | Adding or improving tests |
| `ci/cd` | #5319e7 | CI/CD pipeline improvements |
| `dependencies` | #0366d6 | Dependency updates |

### Priority Labels (How urgent is this?)

| Label | Color | Description |
|-------|-------|-------------|
| `priority: critical` | #b60205 | Must be fixed immediately |
| `priority: high` | #d93f0b | Should be fixed soon |
| `priority: medium` | #fbca04 | Normal priority |
| `priority: low` | #0e8a16 | Can wait |

### Status Labels (What's the current state?)

| Label | Color | Description |
|-------|-------|-------------|
| `status: awaiting-response` | #d876e3 | Waiting for issue author's response |
| `status: in-progress` | #0052cc | Someone is actively working on this |
| `status: blocked` | #b60205 | Blocked by another issue or decision |
| `status: needs-investigation` | #d93f0b | Requires research before implementation |
| `status: duplicate` | #cfd3d7 | Duplicate of another issue |
| `status: wontfix` | #ffffff | Will not be fixed |

### Contributor-Friendly Labels (For newcomers!)

| Label | Color | Description |
|-------|-------|-------------|
| `good first issue` | #7057ff | Good for newcomers (featured on GitHub and goodfirstissue.dev) |
| `help wanted` | #008672 | Extra attention needed from the community |
| `hacktoberfest` | #ff7518 | Eligible for Hacktoberfest (seasonal) |

### Component Labels (Which part of the SDK?)

| Label | Color | Description |
|-------|-------|-------------|
| `component: domain` | #1d76db | Domain layer (entities, rules) |
| `component: ports` | #1d76db | Ports layer (protocols) |
| `component: adapters` | #1d76db | Adapters layer (builders, validators, exporters) |
| `component: application` | #1d76db | Application layer (services, use cases) |
| `component: api` | #1d76db | Public API and CLI |
| `component: docs` | #0075ca | Documentation |
| `component: tests` | #0e8a16 | Test suite |
| `component: tooling` | #5319e7 | Development tools (pre-commit, CI, etc.) |

### Boundary-Related Labels (Critical for SDK scope!)

| Label | Color | Description |
|-------|-------|-------------|
| `boundary: compliant` | #0e8a16 | Complies with platform boundaries |
| `boundary: violation` | #b60205 | Violates platform boundaries (will be rejected) |
| `boundary: needs-review` | #fbca04 | Needs boundary compliance review |

## Labeling Guidelines

### For Maintainers

1. **Every issue/PR should have**:
   - At least one **type label** (bug, enhancement, etc.)
   - At least one **component label** (if applicable)

2. **Add contributor-friendly labels** when:
   - Issue is well-defined and can be done independently
   - Documentation or testing tasks
   - Estimated effort is small (<4 hours)

3. **Priority labels** are optional but helpful for planning

4. **Boundary labels** MUST be applied to:
   - Any feature that might touch execution, billing, or platform authority
   - PRs that add new public APIs

### For Contributors

- Don't worry about labels when creating issues - maintainers will add them
- Look for `good first issue` and `help wanted` to find contribution opportunities
- Check component labels to find issues in areas you're interested in

## Issue Lifecycle Example

```text
1. User creates issue (no labels)
      ↓
2. Maintainer triages: adds type, component, maybe priority
      ↓
3. If suitable for newcomers: add "good first issue"
      ↓
4. Contributor asks to work on it: add "status: in-progress"
      ↓
5. PR submitted: linked to issue automatically closes it
```

## Creating Labels (For Maintainers)

Use GitHub's label interface or the GitHub CLI:

```bash
# Example: Create a label
gh label create "good first issue" \
  --description "Good for newcomers" \
  --color "7057ff"
```

For bulk label creation, see `.github/scripts/create-labels.sh` (if exists).

## References

- [GitHub Labels Documentation](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [Good First Issue](https://goodfirstissue.dev/)
- [Hacktoberfest Label Guidelines](https://hacktoberfest.com/participation/#maintainers)

---

**Questions?** Open a discussion or ask in Discord!
