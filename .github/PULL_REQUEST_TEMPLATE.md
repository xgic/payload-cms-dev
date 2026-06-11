## Description

<!-- Provide a clear and concise description of the changes. -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring / Code cleanup
- [ ] Devcontainer / Infrastructure improvement
- [ ] Release / Versioning work (0.2.0+ – see external contributor simulation process in CONTRIBUTING.md and the 0.2.0 living guide)

## Testing

**Required:** Please confirm the following before requesting review (see TESTING.md and AGENTS.md for current commands):

- [ ] `ruff format . && ruff check .` passes (80-col for code files)
- [ ] `PYTHONPATH=src python -m pytest tests/ -q` passes (or coverage intentionally adjusted)
- [ ] Changes were tested inside the Dev Container
- [ ] `xde check`, `xde env`, and targeted `xde reset --dry-run` + smoke flows were exercised for environment / destructive changes
- [ ] Manual verification of affected `xde` commands (e.g. `xde dev`, `xde setup payloadcms`, `xde reset --yes`) performed where relevant

## Checklist

- [ ] My code follows the style guidelines of this project (see [CONTRIBUTING.md](.github/CONTRIBUTING.md), especially the 80-character line length rule for code files)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation (README, CONTRIBUTING, TESTING.md, etc.)
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally (ruff + pytest)

## AI Assistance (for 0.2.0+ release work and agentic contributions)

- [ ] This PR (or the work leading to it) was drafted/assisted by Grok Build (or similar) using GitHub MCP tools (create_branch, issue_write, create_pull_request draft, push_files, etc.) as part of the external contributor simulation + AI automation process (see approved plan.md "AI Automation of Release Processes" and the "Release Contributions & AI-Assisted Execution" section in CONTRIBUTING.md).
- Human/developer verification steps completed before remote actions (list or link to GitHub comments/approvals): 

## Related Issues

<!-- Link any related issues here (e.g. Fixes #123) -->
