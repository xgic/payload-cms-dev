# Grok Playbooks for XGIC Payload CMS Dev Containers

Concrete workflows for Grok Build and similar agents on this **template**.

**Always start every session with the Session Startup Playbook.**

Follow Collaboration Principles in [AGENTS.md](../AGENTS.md). Multi-repo standards: https://github.com/xgic/ai

---

## Session Startup Playbook (run first)

1. **Read core agent docs** (if not already in context):
   - `AGENTS.md`
   - `docs/architecture.md`
   - [ADR-0005](https://github.com/xgic/ai/blob/main/docs/adr/0005-modular-xgic-cli-and-retirement-of-xde.md) when CLI ownership is unclear

2. **Gather live environment state** (inside Dev Container preferred):
   ```bash
   xgic --help
   xgic check
   xgic payload env
   ```

3. **Inspect template config**:
   ```bash
   ls -la
   head -20 .devcontainer/create-payload-config.json
   git status --short
   ```

4. **Choose the right repo**:
   - Template / Dev Container / compose / thin scripts → **this** repository
   - CLI lifecycle (`up`/`down`/`check`) → https://github.com/xgic/dev-cli
   - Payload product commands (`xgic payload …`) → https://github.com/xgic/payload-cms-cli
   - CLI framework → https://github.com/xgic/cli

**Output to human**: Brief environment summary before proposing next actions.

---

## Playbook: Change template infrastructure

**When**: Dockerfile, compose, Dev Container hooks, thin scripts, CI, template docs.

1. Dedicated issue branch from latest `main` (include issue number).
2. Keep bash shims thin (`exec xgic …` where applicable).
3. Run lint/test gates relevant to the change; manual `xgic check` when touching env flows.
4. Update AGENTS / README / TESTING when user-visible behavior changes.
5. Open PR; human UI review before merge.

---

## Playbook: Implement or change a CLI command

**When**: New or changed `xgic` / `xgic payload` behavior.

**Do not implement CLI logic in this template.**

1. Open work in the owning modular package (cli / dev-cli / payload-cms-cli).
2. Follow that repo’s AGENTS and release process ([python-package-release.md](https://github.com/xgic/ai/blob/main/docs/python-package-release.md)).
3. After a published release, bump consumer pins in this template’s `pyproject.toml` / Dockerfile if required.

---

## Playbook: Release this template

1. Session startup + healthy `xgic check` inside the container.
2. CI green: Lint, Test, Release Validation gates.
3. Follow [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md).
4. Human verification of destructive flows with `--dry-run` first (`xgic payload reset`).
