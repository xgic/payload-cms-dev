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

**Required:** Please confirm the following before requesting review:

- [ ] `make validate` passes locally (lint + tests + schema)
- [ ] `make test-cov` passes (or coverage threshold is intentionally adjusted)
- [ ] Changes were tested inside the dev container (`make test-in-container` if relevant)
- [ ] A full `make rebuild` was performed at least once for significant container changes
- [ ] Manual smoke tests were performed for affected flows (e.g. `make reset-project`, `make create-payload`)

## Checklist

- [ ] My code follows the style guidelines of this project (see [CONTRIBUTING.md](.github/CONTRIBUTING.md), especially the 80-character line length rule for code files)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation (README, CONTRIBUTING, TESTING.md, etc.)
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally with `make validate`

## AI Assistance (for 0.2.0+ release work and agentic contributions)

- [ ] This PR (or the work leading to it) was drafted/assisted by Grok Build (or similar) using GitHub MCP tools (create_branch, issue_write, create_pull_request draft, push_files, etc.) as part of the external contributor simulation + AI automation process (see approved plan.md "AI Automation of Release Processes" and the "Release Contributions & AI-Assisted Execution" section in CONTRIBUTING.md).
- Human/developer verification steps completed before remote actions (list or link to GitHub comments/approvals): 

## Related Issues

<!-- Link any related issues here (e.g. Fixes #123) -->
