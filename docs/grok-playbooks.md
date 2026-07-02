# Grok Playbooks for XGIC Payload CMS Dev Containers

This document contains concrete, step-by-step workflows optimized for Grok Build. Use these as templates when performing common tasks.

**Always start every session by following the "Session Startup Playbook".**

All work documented here must follow the Collaboration Principles defined in `AGENTS.md` (positive tone, constructive framing, reference past only to prevent future mistakes).

---

## Session Startup Playbook (Run This First)

**Goal**: Quickly build accurate shared context with the human developer and reduce the risk of operating on outdated assumptions.

1. **Read the core agent docs** (if not already in context):
   - `AGENTS.md`
   - `docs/architecture.md`
   - `docs/xde-reference.md`

2. **Gather live environment state**:
   ```bash
   xde --help
   xde check
   xde env
   ```

3. **Understand the current working directory and generated project**:
   ```bash
   ls -la
   cat .devcontainer/create-payload-config.json | head -20
   ```

4. **Check for any obvious issues**:
   - Look at recent changes (if in a long session).
   - Run `git status --short` if relevant.

5. **Decide on the right abstraction level**:
   - Prefer `xde` commands.
   - Use `EnvironmentContext` concepts mentally.
   - Only drop to raw `docker compose` or scripts when explicitly migrating logic.

**Output to human**: Briefly summarize the current environment state before proposing next actions.

---

## Playbook: Implement a New xde Command

**When**: Adding new functionality like `xde foo` or enhancing an existing one.

Steps:

1. **Update the surface first** (in `src/xde/cli.py`):
   - Add the parser.
   - Decide on arguments and help text.
   - Make sure it follows the "small surface, predictable defaults" principle.

2. **Create or update the command module**:
   - Prefer `src/xde/commands/<name>.py`.
   - Follow the pattern: `def run_xxx(args, *, env: EnvironmentContext, docker: DockerComposeController) -> int:`

3. **Implement logic**:
   - Push real work into `core/` when possible.
   - Use `DockerComposeController` for any Docker interactions.
   - Add `--dry-run` support for anything destructive or expensive.

4. **Update documentation**:
   - Add to `docs/xde-reference.md`.
   - Update `AGENTS.md` if this changes preferred workflows.
   - Update help text / epilog in `cli.py`.

## Playbook: Planning and Executing a Release (0.2.0+ External Contributor Simulation + AI Automation)

**When**: Any 0.2.0+ release work (MongoDB/multi-adapter in 0.2.0; context detection, library extraction, E2E, stage, TUI, etc. in 0.3.0). This is the living template for demonstrating expertise and providing clear examples (per the approved high-level plan).

**Core principle**: Execute and document *exactly* as a new external contributor would (full steps from the "Step-by-Step Guide" in CONTRIBUTING.md + OSS best practices: GitHub Flow, fork/PR model, milestones, Conventional Commits, PR template, recognition, etc.) *plus* the project's internal AGENTS guidelines (session startup, atomic commits with full func + lint + tests + docs, 80-col, positive tone, update AGENTS.md, platform issues and primary plan when philosophy changes, prefer xde, etc.).

**Grok Build AI automation (unique to this AI-first project)**: Grok heavily automates the mechanical/OSS tasks using its connected GitHub MCP tools (after `search_tool` for schema):
- `grok_com_github__create_branch` (for the feat/ release branch – simulates the "create feature branch" after fork).
- `grok_com_github__issue_write` (method=create) for the release milestone + labeled "ai-draft" issues for sub-tasks (bodies must explicitly instruct to follow this external sim + human gates; link to the plan and this playbook).
- `grok_com_github__create_pull_request` (with `draft: true`) from the branch, with full PR template body + "Closes #xxx" links.
- `grok_com_github__push_files` / `create_or_update_file` for changes (Conventional Commit message in the call).
- `grok_com_github__add_issue_comment`, `pull_request_review_write`, etc. for updates/reviews.
- `run_terminal_command` (gh CLI) as fallback or for anything not covered by MCP.
- **Non-negotiable human/developer verification gates**: After *every* tool call that would make a remote change (branch, issue, PR draft, push, merge), Grok must output the result + clear summary and **pause for explicit human approval** (e.g., "LGTM on GitHub issue #X, proceed with code changes" or comment on the draft). Log all outputs/responses in the session for the audit trail. This ensures correctness, tone, and builds the transparent, professional record that elevates XGIC reputation.

**High-level steps (narrative form – the 0.2.0 living guide in docs/releases/ is the detailed, reusable artifact)**:

1. **Session startup (AGENTS – always)**: `xde --help; xde check; xde env`. Review create-payload-config, git status, recent docs.

2. **Fork simulation + branch (Grok automates via MCP `create_branch` for `feat/0.2.0-xxx` on the repo; document as external fork simulation per CONTRIBUTING. Human approves the branch creation output before any further remote actions.)**

3. **Create high-level + detailed plan** (this playbook + the release-specific guide in docs/releases/, plus update platform issues and primary plan with 0.x section + automation sub-tasks). Human reviews/approves the plan.

4. **Break into atomic, valuable slices** (small-first, per commit rules). For each:
   - Grok drafts the changes (code, tests, docs) + any OSS artifacts (issues, PR body).
   - Human verifies (review diff, run ruff/pytest locally if needed, approve).
   - Grok applies via MCP push / create_or_update on the feat branch (Conventional message).
   - CI must pass (existing lint + test workflows).
   - Update *all relevant docs* in the same commit (CONTRIBUTING, README, AGENTS, playbooks, this guide, etc.).
   - Open/update draft PR via MCP (human approves the `create_pull_request` call).

5. **Address reviews** (Grok can draft responses via MCP review/comment tools; human approves before posting).

6. **Merge** (human gate via MCP `merge_pull_request` or UI, after approval + checks). Grok automates post-merge (platform issues and primary plan "Done", CONTRIBUTORS.md, release notes, etc. – with approval).

7. **Release artifacts + announcement**. The full GitHub history (issues with ai-draft labels, branch, draft PRs, clean commits) + this guide + the session plan become the "clear example for future contributors".

**Grok-specific examples** (adapt for any release):
- "Using the MCP tools after search, create a draft issue for [sub-task] with labels ['0.2.0', 'ai-draft', 'enhancement'], body that quotes the external sim requirement from CONTRIBUTING + this playbook, and notes 'Human verification required before code or PR'."
- "After human approval on the issue, use `push_files` on the feat branch with a full Conventional Commit message that includes the change + docs update + test results."
- "Draft the PR with `create_pull_request` (draft: true, full template, Closes links). Log the URL for human review before any merge."

**Documentation updates required in the same atomic commits as code**: See the "Updated Documentation Tasks" in the session plan.md (CONTRIBUTING, README, AGENTS, playbooks, PR template, new release guide artifact, platform issues and primary plan, etc.). All must stay positive, scannable, and aligned with the mission.

**Risks / Considerations** (document for transparency): Scope creep (stick to high-level + smallest valuable slices); human gates are mandatory (AI drafts are high-quality but not infallible); as owner, the "fork" is simulated for the example value – the public record still demonstrates the full external flow.

**Success**: The release produces not just the feature (e.g. working MongoDB support), but a complete, auditable, impressive set of artifacts (guide, history, automation logs) that future contributors can follow and that visibly elevates the project's and XGIC's reputation. Repeat for 0.3.0+ (80%+ automation once the template exists).

See the approved session plan.md for the full 0.2.0/0.3.0 high-level scopes, risks, success criteria, and Grok GitHub capability enhancements. This playbook was added as part of that planning.

(End of new release playbook.)

5. **Add agent-friendly touches**:
   - Good success/failure messages with next steps (use Rich panels).
   - Consider `--json` output if the command produces structured data.
   - Clear error messages.

6. **Test mentally**:
   - Can another agent discover and use this command easily from `--help` and docs?

---

## Playbook: Migrate Logic from Legacy Script into xde

**When**: Moving functionality from legacy scripts (e.g. the former `reset-project.py`), `regenerate-env.py`, or shell scripts.

**Note**: The `reset-project.py` migration is complete; the script and its dedicated fidelity tests have been removed. The playbook below is retained for future similar work.

Steps:

1. **Understand the current behavior deeply**:
   - Read the legacy code.
   - Run it with `--dry-run` or equivalent if available.
   - Document edge cases in `AGENTS.md`.

2. **Extract pure functions first**:
   - Move logic into `src/xde/core/` or `src/xde/models/`.
   - Make them testable and side-effect free where possible.

3. **Create the new command surface**:
   - Add to `cli.py`.
   - Implement in `commands/`.
   - Keep backward compatibility during transition if needed (thin wrapper).

4. **Preserve safety**:
   - The legacy `reset-project.py` has very careful logic around credentials. Do not regress this.

5. **Update guidance**:
   - Mark the old location as "legacy — prefer `xde <command>`" in comments and docs.
   - Update `AGENTS.md` "Current State" section.

6. **Test the migration path**:
   - Can both old and new paths be used during transition?

---

## Playbook: Debug a Broken Development Environment

**When**: Human reports "it doesn't work" or `xde dev` fails.

Recommended sequence:

1. `xde check` — Get structured diagnosis.
2. `xde env` — Check for credential / config issues.
3. Review recent changes (git log, recent file modifications).
4. If reset-related: `xde reset --dry-run` and analyze output.
5. Check container logs: `xde logs` (or raw if needed).
6. Inspect the generated Payload project state.
7. Propose the smallest safe fix first (often `xde reset` or credential regeneration).

Always explain the root cause hypothesis to the human before acting.

---

## Playbook: Add or Modify Configuration Options

**When**: Extending `create-payload-config.json` (e.g., new template options, agent features).

Steps:

1. **Update the source of truth**:
   - ` .devcontainer/config/types.ts` (Zod schema + types).

2. **Regenerate the JSON Schema**:
   - Run the generator (or `xde schema generate` once available).

3. **Update consumers**:
   - `setup-payload.sh`
   - Any Python config loaders in `src/xde/`
   - Documentation and examples.

4. **Consider agent impact**:
   - Does this new option make it easier or harder for agents to generate projects?
   - Add clear descriptions in the schema (these become editor hover docs).

5. **Update AGENTS.md** if this changes how agents should interact with project creation.

---

## Common Pitfalls in This Project (For Grok)

- Assuming we're always inside the container (use `EnvironmentContext`).
- Reaching for retired scripts or raw low-level commands (docker/shell) instead of `xde`.
- Being too aggressive with credential rotation (this has caused authentication problems in the past).
- Forgetting that the generated Payload project is a separate folder, not inside `.devcontainer`.
- Underestimating how valuable good `--dry-run` and clear next-step messages are for both humans and agents.
- Treating `xg/` (reference material on the `reference/xg-ais` branch) as active code.

---

## How to Help Evolve the Agent Foundation

While working, note opportunities to improve:

- New commands that would reduce friction for agents.
- Areas where context is missing or unclear.
- Commands that would benefit from `--json` output.
- Documentation that is hard to navigate.

Propose small, targeted improvements to `AGENTS.md` and the `docs/` folder. These changes compound quickly.

---

**Use these playbooks as living templates.** Update them when you discover better patterns.

This document exists to make Grok (and similar agents) dramatically more effective at building high-quality Payload CMS projects using this template.