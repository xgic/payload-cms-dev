# Testing Strategy for XGIC Payload CMS Dev Containers

## Current State (as of 0.1.0)

- **Unit test coverage**: 59% overall (will rise with new Makefile tests)
  - `tests/`: 100% (existing Python tests + new `tests/make/` macro tests)
  - `reset-project.py`: 41%
  - `get-payload-project-name.py`: 0%
  - `regenerate-env.py`: 0%
- **Integration/smoke testing**: `devcontainer-tests.sh` (version + connectivity checks)
- **Python code under test focus**: `reset-project.py` (highest value/complexity) + supporting config helpers

> **Note on Python test tooling**: `pytest`, `pytest-cov`, and `pytest-mock` are **not** pre-installed in the base container image (to keep it lean). They are installed on-demand the first time you run `make test`, `make test-cov`, or `make validate`. See the `ensure-dev-python` target in the Makefile.

## Testing Philosophy

This is a **Dev Container + DX tooling** repository, not a traditional application.

**Priorities (in order):**

1. **Reliability of destructive operations** (`reset-project.py`)
2. **Correctness of credential and config handling**
3. **Schema validation** (for excellent VS Code DX)
4. **Smoke testing** of the container environment
5. High line coverage on shell scripts (low priority — hard to test meaningfully)

## Recommended Coverage Targets (for future work)

| Component                    | Target Coverage | Rationale |
|-----------------------------|------------------|---------|
| `reset-project.py` (core logic) | 70%             | Most complex + dangerous code (currently 41%) |
| `regenerate-env.py`         | 60%             | Credential generation is security-adjacent (currently 0%) |
| Config loading helpers      | 80%             | Small and critical |
| Shell scripts               | Not measured    | Use `devcontainer-tests.sh` + manual verification |
| Overall project             | **60%**         | Current CI floor (we are at 59% as of 0.1.0 with focused testing) |

## Running Tests

```bash
# Inside the dev container (recommended)
make test
make test-make         # Dedicated Makefile guard/delegation/@-leakage tests
make test-cov          # Generates htmlcov/ + enforces 60% threshold
make validate          # Full lint (incl. checkmake) + test + schema validation
```

As of 0.1.0 we achieve 59% overall coverage with the current focused test suite.

## Adding New Tests

- Place unit tests in `tests/`
- Use `pytest` + `pytest-mock` for filesystem and subprocess mocking
- Prefer testing pure functions over side-effect heavy code
- Integration behavior is covered by `devcontainer-tests.sh` + `make rebuild`

**AI assistants**: See [AGENTS.md](AGENTS.md), [docs/architecture.md](docs/architecture.md), and [docs/xde-reference.md](docs/xde-reference.md) for testing priorities, architecture, and recommended commands.

## Makefile Behavior Testing (New in 0.1.x)

The most complex and historically bug-prone part of the project is the **Makefile** itself — specifically the `HOST_ONLY_GUARD` and `RUN_IN_CONTAINER` macros, context detection via `REMOTE_CONTAINERS` / `CODESPACES` / `XG_AIS_HOST_TYPE`, and delegation logic.

### Why dedicated Makefile tests exist

Traditional "make test" only exercises Python. After several painful delegation bugs (including the literal `@make` executable-not-found incident), we added first-class tests for the Makefile's *observable behavior*.

### How it works

- Tests live in `tests/make/` (self-contained minimal Makefiles that embed the exact macro definitions under test).
- Heavy use of `pytest-subprocess` + environment variable matrices to simulate host vs. dev container execution contexts.
- Explicit regression tests ensure a leading `@` is **never** passed through `$(call RUN_IN_CONTAINER, ...)` (the root cause of the `@make` failure).
- Exact user-facing error messages are asserted so the delegation UX stays excellent.

### Running the Makefile tests

```bash
# All of the following run the new Makefile tests:
make test-make
make test-makefile
make test               # includes them via the normal test path
make validate           # runs them as part of full validation
```

The tests are fast, run both on the host and inside the container, and are enforced in CI.

### Adding new Makefile tests

- Add tests in `tests/make/test_*.py`
- Use the fixtures in `tests/make/conftest.py` (`minimal_makefile_with_macros`, `run_make`, etc.)
- For new macro behavior, prefer writing small isolated test Makefiles over testing the full real Makefile (much less brittle).
- Always add a regression test when you touch `HOST_ONLY_GUARD`, `RUN_IN_CONTAINER`, or any recipe that uses `$(call ...)` delegation.

## CI Enforcement

Python tests + coverage run on every push and pull request via `.github/workflows/test.yml`.

As of the 0.1.0 release we have 59% overall coverage. The CI job (and `make test-cov`) will fail if coverage drops below the 60% floor.

## Future Improvements (Post 0.1.0)

- Add property-based testing for config parsing edge cases
- Golden file tests for generated `.env` content
- More robust Docker mocking for `reset_postgres` flows
- Tighten `checkmake` rules in CI (currently advisory) and expand Makefile test coverage to more real targets
- Consider adding a small Bats suite under `tests/make/` later if pure-shell contributors want it (pytest remains the primary harness)

---

**Goal**: High confidence in the most dangerous parts of the tooling, without turning a Dev Container template into a heavily-tested Python project.
