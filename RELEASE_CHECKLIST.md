# XGIC Payload CMS Dev Containers — Release Checklist (0.2.0+)

This checklist is for preparing and executing releases on the modern `release/0.X.0` branch model (see "Release Contributions & AI-Assisted Execution" in [CONTRIBUTING.md](.github/CONTRIBUTING.md) and the living guide in `docs/releases/0.2.0-...-external-contributor-guide.md`).

**0.1.0 was the last "big-bang" initial public release** (orphan branch + history reset). All subsequent releases (0.2.0 MongoDB/multi-adapter, 0.3.0+, etc.) follow the release-branch accumulation process:
- Cut `release/0.2.0` (or equivalent) from `main` (after the previous release is merged).
- All work (code, tests, docs, automation artifacts) targets the release branch via PRs.
- Only when the *entire* release scope is complete (functionality + tests + documentation + living examples) do we perform the final merge `release/0.X.0` → `main` + tag.
- Full external contributor simulation + Grok Build MCP automation **with mandatory human verification gates** at every remote action.
- Every commit: atomic, Conventional, includes full functionality + ruff + relevant tests + doc updates (per AGENTS.md).

> **Session Startup (mandatory)**: At the start of any planning or implementation session (inside the Dev Container):
> ```bash
> xde --help
> xde check
> xde env
> ```

> **Automation Note**: Ruff + pytest run in CI on every PR. `xde` commands replace most old `make` targets for environment validation. Human judgment + living docs are still essential for release quality and the "agent ergonomics" mission.

## 1. Session & Environment Health (Start Here — Every Time)
Inside the Dev Container:
```bash
xde --help
xde check
xde env
xde reset --dry-run
```

- [ ] `xde check` reports healthy services + DB connectivity (Postgres or chosen adapter) + expected project folder.
- [ ] `xde env` shows sensible configuration (no surprises in secrets or generated values).
- [ ] `xde reset --dry-run` produces a clear, accurate blast-radius description.

## 2. Code & Test Quality Gates (Run on Every Commit)
```bash
ruff format .
ruff check .
PYTHONPATH=src python -m pytest tests/ -q --tb=line
# For coverage (when relevant):
# PYTHONPATH=src python -m pytest tests/ --cov=src/xde --cov-report=term-missing
```

- [ ] Ruff passes (80-col for code files only; Markdown is exempt).
- [ ] All relevant tests pass (focus on `src/xde/core/`, reset/setup flows, config handling, and any new 0.2.0+ logic).
- [ ] New/changed behavior includes tests (prefer pure functions where possible — see `tests/test_project.py` patterns).
- [ ] The commit also updates relevant documentation in the same atomic change (AGENTS, platform issues and primary plan, living release guide, README Planned Extensions, TESTING.md, etc.).

**Note**: Use the direct commands shown above (or `xde` where it provides environment validation).

## 3. xde-Specific & Destructive Flow Validation **[Manual — High Value]**
These are the modern equivalents of the old "reset + create" manual tests. Always start with `--dry-run`.

Inside the container:
- [ ] `xde reset --dry-run` (review impact on Postgres volume + generated project dir).
- [ ] `xde setup payloadcms` (or the postStart hook) produces a complete, working project (or is idempotent on an existing one).
- [ ] `xde reset --yes` followed by `xde dev` (or `xde setup payloadcms` + `xde dev`) results in a running Payload app that connects to the database.
- [ ] Test with the target DB adapter for the release (e.g. for 0.2.0: switch `dbAdapter` to `mongodb` in `create-payload-config.json`, ensure Mongo service + client work, generated app uses the correct adapter).
- [ ] `xde check` and `xde env` remain accurate after reset/setup/dev cycles.
- [ ] Generated `create-payload-config.json` (and schema) produce good editor IntelliSense.
- [ ] No regression in the default Postgres path.

**Safety rule**: Never run destructive `xde reset` / `xde clean` without `--dry-run` first during release validation.

## 4. Documentation & Living Artifacts Synchronization **[Manual]**
- [ ] README.md "Planned Extensions (Post v1)" and "The xde CLI" table are current for the release.
- [ ] The release-specific living guide (`docs/releases/0.2.0-...-external-contributor-guide.md`) accurately reflects scope, risks, success criteria, automation steps taken, and human gates.
- [ ] CONTRIBUTING.md "Release Contributions & AI-Assisted Execution" section + Step-by-Step Guide are consistent with actual practice.
- [ ] AGENTS.md, the primary plan and platform issues/tasks (Future Releases section), TESTING.md, and this checklist itself are updated if the process or philosophy changed.
- [ ] No stale references to retired automation, old scripts, or pre-`xde` workflows.
- [ ] License section (README + LICENSE file) is correct (Apache 2.0 as of late 0.1.0/0.2.0 era).

## 5. Git, Branching & Release Hygiene (Current Model)
- [ ] You are on (or PRs target) the correct `release/0.2.0` (or equivalent) branch cut from the tip of `main` (after the previous release).
- [ ] All commits on the release branch are atomic + Conventional + pass ruff + relevant tests + include doc updates.
- [ ] History on the release branch is reasonably clean (local small commits are fine; major squashing happens before the final release-to-main merge).
- [ ] No stray release artifacts (`COVERAGE_REPORT*`, old `COMMIT_MESSAGE*`, temp files, etc.).
- [ ] `.gitignore` still correctly excludes generated apps (`website/` etc.), coverage, `.env*`, node_modules at root, etc.
- [ ] The full external-sim + Grok automation audit trail exists (issues with "ai-draft" + human gate language, draft PRs, branch, comments, MCP logs in session plan if used).

**For the final release merge (when the release branch is *complete*)**:
- [ ] Living guide, platform issues and primary plan "Done" items, README Planned Extensions, and any changelogs/release notes are finalized.
- [ ] Open (or directly perform) the final PR/merge from `release/0.2.0` → `main`. (This is the key human gate / "PR approval" that the entire release scope is complete.)
- [ ] **Standard automated tagging task (after the merge lands on main)**: Create an annotated tag on the *exact* merge commit. Grok proposes the command (preferably `gh release create` which creates both the annotated tag and the rich GitHub Release in one step; derive title/notes from the finalized living guide + this checklist). Human explicitly approves (LGTM/comment). Grok executes via terminal + pushes. Tag message must reference the release scope, living guide, and key artifacts.
  - Example (Grok will adapt): `gh release create v0.2.0 --target main --title "v0.2.0 — ..." --notes "..." `
  - Or: `git tag -a v0.2.0 -m "..." && git push origin v0.2.0 && gh release create v0.2.0 ...`
- [ ] Confirm the tag points to the correct merge commit on main and the GitHub Release is published with links to the living guide, milestone, and major PRs/issues.
- [ ] (Post-tag) Update any remaining "Done" items, CONTRIBUTORS.md, etc. (Grok automates with human approval).

## 6. Specific Release Success Criteria (0.2.0+ Example)
See the detailed criteria in the release's living guide (`docs/releases/0.2.0-...`).

Typical items:
- [ ] New DB adapter (e.g. Mongo) works end-to-end via `create-payload-config.json` → `xde setup payloadcms` (or reset) → `xde dev`.
- [ ] Default (Postgres) path is 100% unchanged and tested.
- [ ] Docker changes (compose profiles, client tools) are minimal and documented.
- [ ] All `xde` commands (`check`, `env`, `reset`, `dev`, etc.) behave correctly for the new capability.
- [ ] E2E smoke of the generated app (HTTP on :3000, admin reachability, DB connectivity) succeeds for the target adapter(s).
- [ ] Documentation + automation examples are complete enough for the next agent or external contributor to follow.

## 7. Post-Release
- [ ] GitHub Release created with links to the living guide, milestone, and major PRs.
- [ ] Repo topics, description, and README badges reflect the new version if appropriate.
- [ ] The primary plan and platform issues/tasks and the next release's planning artifacts (new living guide stub, milestone) are prepared.
- [ ] Any "hall of fame" / CONTRIBUTORS.md updates (if maintained) are done.
- [ ] Consider a lightweight blog post or social note highlighting the release + the external-sim process (reputation building).

## Historical Note (v0.1.0 Only)
The original "history reset using `git checkout --orphan`" and one-time initial public commit process applied **only** to the very first public release of 0.1.0 (tagged at merge commit 671a8e5 on main). They are no longer used. The current model (release branches + external simulation + `xde` + living guides + annotated tag on the release merge commit) applies for all future releases (v0.2.0+).

---

**Goal:** A clean, professional, and trustworthy first public release.

---

## Automation & Tooling Notes (Current State)

- **CI Gates** (run on every PR to a release branch or main): Ruff (format + check) + `PYTHONPATH=src python -m pytest`. Enforced. Any commit touching code must pass.
- **Environment Validation**: Use `xde check`, `xde env`, `xde reset --dry-run`, and `xde dev` (or the thin `setup-payload.sh` hook). These are the repeatable, human-friendly ways to validate the dev container experience.
- **Hard to fully automate** (still require thoughtful human + inside-container time):
  - End-to-end "I just cloned and it feels great" experience (including `xde dev` stopping cleanly on Ctrl+C).
  - Generated app behavior for new adapters (Mongo vs Postgres differences in Payload).
  - Quality of editor IntelliSense for `create-payload-config.json` + schema.
  - The overall "agent can be productive in minutes" feel.
- **Grok / AI Automation (0.2.0+)**: Heavily used for drafting branches, issues, PRs, file changes, and living docs via GitHub MCP tools. **Every remote action requires explicit human approval** before execution. This is documented in the living guide and is a core part of the reputation/leading-by-example goal.
- **Living Documentation > Static Checklist**: For any given release, the primary detailed artifact is the release-specific guide under `docs/releases/`. This checklist is the high-level repeatable process + safety net. Update both when the workflow evolves.
- **Future**: As E2E coverage grows (generated apps + Playwright), more of the "manual developer workflows" section can move into automated jobs. The human checklist will shrink but never disappear for the irreplaceable UX and safety reviews.

**Goal**: Every release (0.2.0, 0.3.0, ...) produces a clean, professional, trustworthy result *and* a set of clear, followable examples (the branch, issues, PRs, living guide, and this updated checklist) that demonstrate both technical excellence and excellent open-source process. This directly supports the mission of being the #1 foundation for building web apps with Grok Build and similar agentic tools.
