# Grok Playbooks for XGIC Payload CMS Dev Containers

This document contains concrete, step-by-step workflows optimized for Grok Build. Use these as templates when performing common tasks.

**Always start every session by following the "Session Startup Playbook".**

---

## Session Startup Playbook (Run This First)

**Goal**: Quickly build accurate context and reduce hallucination risk.

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

5. **Add agent-friendly touches**:
   - Good success/failure messages with next steps (use Rich panels).
   - Consider `--json` output if the command produces structured data.
   - Clear error messages.

6. **Test mentally**:
   - Can another agent discover and use this command easily from `--help` and docs?

---

## Playbook: Migrate Logic from Legacy Script into xde

**When**: Moving functionality from `reset-project.py`, `regenerate-env.py`, shell scripts, or Makefile targets.

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
- Reaching for the old Makefile or raw Python scripts instead of `xde`.
- Being too aggressive with credential rotation (this has caused authentication problems in the past).
- Forgetting that the generated Payload project is a separate folder, not inside `.devcontainer`.
- Underestimating how valuable good `--dry-run` and clear next-step messages are for both humans and agents.
- Treating `xg/` as active code (it is reference only).

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