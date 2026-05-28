## Description

<!-- Provide a clear and concise description of the changes. -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring / Code cleanup
- [ ] Devcontainer / Infrastructure improvement

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

## Related Issues

<!-- Link any related issues here (e.g. Fixes #123) -->
