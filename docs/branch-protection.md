# Branch Protection Policy (main and release/* branches)

**Purpose**: Protect the integrity of `main` (the source of truth for releases, tags, and the published history that underpins reproducible dev containers and OSS reputation) and active `release/*` branches (the long-lived accumulation branches used during a release cycle, e.g. `release/0.2.0`).

This follows GitHub best practices, OSS standards, and the project's own principles (immutable/clean history via Conventional Commits + linear history, automated gates via CI, mandatory review + human verification for all changes, excellent support for both human contributors and Grok Build / AI-assisted workflows).

## Current Model (0.2.0+)

- `main` is protected and receives only final, fully validated merges (typically the end-of-release merge from a `release/0.X.0` branch + tags).
- During a release cycle, the semantic long-lived branch (e.g. `release/0.2.0`) is the primary target for ongoing work, PRs (including external contributor simulations and Grok-automated changes), and accumulation. It receives equivalent protection.
- Short-lived branches (feature/fix/docs/etc.) are created from the current base (usually the active release branch or main) and merged via PR only.
- All changes follow the rules in [CONTRIBUTING.md](../.github/CONTRIBUTING.md), [AGENTS.md](../AGENTS.md), and the release-specific living guide (e.g. `docs/releases/0.2.0-...`).

See also:
- [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md) (environment validation, gates).
- The living release guide for how external-sim + Grok MCP automation interacts with these branches.

## Recommended Rules (GitHub Rulesets)

Use **Repository rulesets** (modern, flexible, fnmatch targets, bypass lists, easy to toggle).

### For `main`
- **Name**: `Protect main` (or similar).
- **Enforcement**: Active (or start Disabled for testing).
- **Bypass list**: Your primary owner/admin account + Repository admins role. Strongly consider the "For pull requests only" option on the bypass so even admins normally go through PRs.
- **Target**: Include `main` (or `refs/heads/main`).
- **Rules to enable**:
  - Restrict deletions
  - Block force pushes
  - Require a pull request before merging (at least 1 approving review; dismiss stale approvals on new commits)
  - Require linear history (pairs with Conventional Commits + rebase/squash merge strategy)
  - Require status checks to pass (see below) + "Require branches to be up to date before merging"
  - Require signed commits (recommended for auditability and professional signal)

- **Status checks to require** (add the actual job names from your workflows; they run on PRs to the protected branch):
  - Lint jobs from `.github/workflows/lint.yml` (shellcheck, actionlint, shfmt, yamllint, etc.)
  - Test / pytest jobs from `.github/workflows/test.yml`
  - Dev container / release validation jobs from `.github/workflows/release-validation.yml` when relevant
  - Any future aggregate "validate" or "ci" job

### For active release branches (e.g. during 0.2.0 development)
Create a parallel ruleset (or one ruleset with multiple targets) for `release/*` (fnmatch `release/*` or specific `release/0.2.0` while it is active).

Use the **same rules** as `main`. This ensures the heavy work of a release (including Grok-automated slices, external contributor PRs, etc.) receives the same gates before the final merge to `main`.

You can have more granular rulesets later (e.g. stricter on main, slightly different bypass windows on a release branch).

## How This Supports Grok Build and Agent Workflows

Strict branch protection is **beneficial** for Grok efficiency and correctness:

- It automatically enforces the project's core commit rules (atomic + Conventional + full lint + relevant tests before anything lands on a protected branch).
- It makes the documented "non-negotiable human/developer verification gates" (see AGENTS.md and playbooks) visible and mechanical: Grok can (and does) create draft PRs, push changes, open issues, etc., via MCP tools (`create_branch`, `push_files`, `create_pull_request` draft=true, etc.), but the protection + "require review + status checks" + human approval step before merge (or before certain bypass actions) prevents any automation from bypassing process.
- Linear history + signed commits + up-to-date requirement produce clean, bisectable, auditable history — exactly what is needed for the "living example" external-sim releases and long-term reputation.

Grok sessions always start with the startup checklist and respect the gates. Protection makes mistakes (e.g. landing unverified work) much harder.

## CODEOWNERS (Recommended)

Create `.github/CODEOWNERS` (committed) and enable "Require review from Code Owners" in the rules.

Example starter (adjust to your team):

```
# Critical infrastructure and agent-optimized foundations
/.devcontainer/         @owner
/src/xde/               @owner
/.github/workflows/     @owner
/docs/                  @owner
/.github/CONTRIBUTING.md @owner
```

This is especially valuable for the dev container definition, the `xde` CLI (the single source of truth), and automation.

## Setup / Maintenance Notes

1. Apply via GitHub UI (Settings → Rules → Rulesets → New ruleset) following the structure above. Rulesets are forward-compatible and work on private repos (full enforcement may require Team plan or public visibility).
2. After creating the ruleset(s), test the happy path: create a short-lived branch (from the current base), make an atomic Conventional commit that passes ruff + pytest, push, open PR, get the required review + see checks pass, then merge (rebase or squash to keep linear).
3. When adding new required CI jobs, update this document *and* add the job name(s) to the ruleset status checks.
4. For emergency hotfixes on a protected branch, use the bypass list (with "for PRs only" preferred for day-to-day).

The actual rules live in GitHub settings (not in this repo as executable code). This document is the source of truth for *policy*, rationale, and how the rules interact with the project's release model + AI-assisted workflows.

## References

- [CONTRIBUTING.md](../.github/CONTRIBUTING.md)
- [AGENTS.md](../AGENTS.md) (especially Collaboration Principles, commit discipline, Grok-specific workflows, and human gates for automation)
- [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md)
- Release living guides under `docs/releases/`
- GitHub docs on rulesets and branch protection

---

**Last updated**: 2026 (aligned to `release/0.2.0` model, xde as primary interface, current CI, and Grok + human-gate automation patterns).

This policy helps keep the project the best possible foundation for building serious Payload CMS apps with Grok Build and similar tools.