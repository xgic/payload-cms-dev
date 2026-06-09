# XGIC Payload CMS Dev Containers — v0.1.0 Release Checklist

Use this checklist before performing the history reset and creating the initial public commit for v0.1.0.

> **Automation Note**: Items marked **[Automated]** can (and should) be run via CI or `make` targets.  
> Items marked **[Manual]** require human judgment and should be done inside the actual dev container.

## Pre-Release Verification (Run in this order)

### 1. Fast Local Quality Gate **[Automated]**
```bash
make validate
```
- [ ] All checks pass (lint + tests + schema validation)
- [ ] Coverage is at or above the 60% threshold

### 2. Full End-to-End Rebuild (Critical) **[Semi-automated]**
From the **host** (recommended to also run in CI via devcontainer CLI):
```bash
make clean
make rebuild
```
- [ ] Container builds successfully
- [ ] `setup-payload.sh` runs non-interactively without prompts
- [ ] Generated Payload project starts with `pnpm dev` and connects to Postgres

**Dockerfile Development Tip**: When actively editing the Dockerfile, use `make docker-build-only-nocache` for much faster iteration instead of full `make rebuild`.

### 3. Inside-Container Validation **[Automated via `make`]**
Once inside the container:
```bash
make validate
make test-cov
make devcontainer-tests
```
- [ ] All targets pass cleanly

### 4. Manual Developer Workflows **[Manual - High Value]**
Inside the container, test these flows (these are difficult to fully automate):

- [ ] `make reset-project YES=1` → `make create-payload`
- [ ] `make reset-project --rotate-credentials YES=1`
- [ ] `make reset-project --dry-run -v`
- [ ] Open generated project → `pnpm dev` works
- [ ] `create-payload-config.json` has good VS Code IntelliSense (hover docs, autocomplete)

### 5. Documentation Review **[Manual]**
- [ ] README.md is clear for new users
- [ ] CONTRIBUTING.md is up to date
- [ ] TESTING.md accurately reflects current test coverage and strategy
- [ ] No references remain to deleted files (e.g. old `post-create.sh`)
- [ ] `make help` output looks professional

### 6. Git & Release Hygiene **[Mostly Automated + Manual Review]**
- [ ] Run final cleanup sweep (see below)
- [ ] Review `.gitignore` (ensure `htmlcov/`, `.coverage`, etc. are ignored)
- [ ] Check for any leftover release artifacts (`COVERAGE_REPORT*`, `COMMIT_MESSAGE*`, etc.)
- [ ] All changes are committed

### 7. Dockerfile / Build Optimization (Recommended for v0.1.0)
- [ ] Use `make docker-build-only-nocache` when actively editing the Dockerfile (much faster than full rebuilds)
- [ ] Use `make docker-build-only` for normal cached image builds during development
- [ ] Consider the layered caching improvements and .dockerignore (see recent changes)
- [ ] Verify that `.dockerignore` is properly excluding unnecessary files (it is now committed)

## Final Cleanup Sweep (Run before history reset)
```bash
# Remove local build artifacts
rm -rf htmlcov .coverage coverage.xml
rm -f COVERAGE_REPORT_0.1.0.txt COMMIT_MESSAGE_0.1.0.txt

# Optional: Clean generated Payload projects if you want a pristine repo
# rm -rf my-payload-cms website
```

## History Reset & Initial Commit
1. `git checkout --orphan temp-main`
2. `git add -A`
3. `git commit -F COMMIT_MESSAGE_0.1.0.txt` (or write a strong message)
4. `git branch -M main`
5. `git push --force origin main`

## Post-Release (After pushing v0.1.0)
- [ ] Verify GitHub Actions (Lint + Test workflows) pass on main
- [ ] Create the first GitHub Release (v0.1.0)
- [ ] Update repo description and topics on GitHub
- [ ] Consider adding a `CODE_OF_CONDUCT.md` and `SECURITY.md` if not present

## Recommended Makefile Targets for Daily Work & Release Prep
- `make docker-build-only-nocache` → Best for active Dockerfile development
- `make docker-build-only` → Normal cached image builds
- `make rebuild YES=1` → Non-interactive full rebuild (for release validation)
- `make pre-release-check` → Quick automated part of the checklist
- `make validate` → Your primary daily quality gate (lint + tests + schema)

---

**Goal:** A clean, professional, and trustworthy first public release.

---

## Automation Opportunities (Best Practices for Dev Container Templates)

For projects like this (Dev Container + Makefile + Python tooling), the community best practice is:

### What Should Be Automated (High ROI)
- `make validate` → Run on every PR (already done via GitHub Actions)
- Python unit tests + coverage enforcement
- ShellCheck + other linters
- JSON Schema validation
- Basic devcontainer build test (using `devcontainer` CLI or `docker compose build`)
- Conventional Commits + semantic release (optional but excellent for future releases)

### What Is Hard / Expensive to Fully Automate
- True "human developer experience" testing inside VS Code
- End-to-end verification of `pnpm dev` in the generated Payload app
- Visual / IntelliSense quality of the JSON schema
- Overall "feel" of the devcontainer

### Recommended Automation Setup for v0.1.0+
1. Strengthen CI with a dedicated "Release Validation" workflow (can be triggered manually before tagging).
2. Use the official `@devcontainers/cli` in CI to build and validate the devcontainer definition.
3. Keep a human-run checklist (this document) for the irreplaceable manual steps.
4. Consider GitHub's "Release Please" or `semantic-release` in the future for automated changelogs + releases.

**Current State**: You already have good foundations (`lint.yml` + `test.yml`). The main gap is a repeatable way to test the full container build in CI.
