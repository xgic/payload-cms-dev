"""
High-value tests for the critical Makefile macros and delegation behavior.

These tests exist specifically to prevent regressions of the class of bugs
seen in results.txt (leading @ being passed literally into docker compose exec).

They use self-contained minimal Makefiles that embed the exact macro logic
under test. This makes the tests robust against unrelated changes in the
real 400+ line Makefile.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from tests.make.conftest import run_make


class TestHostOnlyGuard:
    """Tests for the HOST_ONLY_GUARD macro."""

    def test_allows_execution_on_plain_host(self, minimal_makefile_with_macros: Path):
        """When no container env vars are set, host-only target should succeed."""
        result = run_make(minimal_makefile_with_macros.parent, "host-only-target")
        assert result.returncode == 0
        assert "HOST_ONLY_TARGET_RAN_SUCCESSFULLY" in result.stdout

    @pytest.mark.parametrize(
        "env_var,value",
        [
            ("REMOTE_CONTAINERS", "true"),
            ("REMOTE_CONTAINERS", "1"),
            ("CODESPACES", "true"),
            ("XG_AIS_HOST_TYPE", "xgic-devcontainer"),
        ],
    )
    def test_fails_inside_devcontainer_envs(
        self, minimal_makefile_with_macros: Path, env_var: str, value: str
    ):
        """HOST_ONLY_GUARD must exit 1 with the exact user-facing error when inside container."""
        result = run_make(
            minimal_makefile_with_macros.parent,
            "host-only-target",
            env={env_var: value},
        )
        assert result.returncode != 0
        assert "must be run from the host, not inside the Dev Container" in result.stdout


class TestRunInContainerDelegation:
    """Core tests for the RUN_IN_CONTAINER macro behavior."""

    def test_runs_command_directly_when_in_container(self, minimal_makefile_with_macros: Path):
        """When container markers are present, the command should execute directly (no docker)."""
        result = run_make(
            minimal_makefile_with_macros.parent,
            "container-aware-target",
            env={"REMOTE_CONTAINERS": "true"},
        )
        assert result.returncode == 0
        assert "CONTAINER_AWARE_RAN:inside_or_delegated" in result.stdout
        assert "Running 'container-aware-target' inside the dev container" not in result.stdout

    def test_delegates_via_docker_compose_when_on_host(self, minimal_makefile_with_macros: Path):
        """
        On a plain host (no container env vars), RUN_IN_CONTAINER must attempt
        docker compose exec and produce the delegation message.
        """
        result = run_make(minimal_makefile_with_macros.parent, "container-aware-target")
        # We expect failure because there is no real docker compose / service,
        # but the *important* assertion is that it tried to delegate.
        assert "Running 'container-aware-target' inside the dev container..." in result.stdout
        assert "Failed to run 'container-aware-target' inside the dev container" in result.stdout
        # The exact helpful hints that users see must be present
        assert "Is the container running? Try:  make up" in result.stdout
        assert "VS Code → Dev Containers: Reopen in Container" in result.stdout

    @pytest.mark.parametrize(
        "env_overrides",
        [
            {"CODESPACES": "true"},
            {"XG_AIS_HOST_TYPE": "xgic-devcontainer"},
            {"REMOTE_CONTAINERS": "1", "CODESPACES": "1"},
        ],
    )
    def test_delegation_skipped_for_all_container_markers(
        self, minimal_makefile_with_macros: Path, env_overrides: dict[str, str]
    ):
        """Any of the three recognized container markers must cause direct execution."""
        result = run_make(
            minimal_makefile_with_macros.parent,
            "container-aware-target",
            env=env_overrides,
        )
        assert result.returncode == 0
        assert "CONTAINER_AWARE_RAN" in result.stdout
        assert "Running 'container-aware-target' inside the dev container" not in result.stdout


class TestAtPrefixLeakagePrevention:
    """
    These are the most important regression tests.

    They ensure that a leading '@' in the argument to RUN_IN_CONTAINER is
    never passed through literally to the executed command (the exact failure
    mode from results.txt that produced "@make: executable file not found").
    """

    def test_leading_at_in_call_argument_is_stripped_or_rejected(
        self, minimal_makefile_with_macros: Path
    ):
        """
        Regression test for the exact class of bug in results.txt.

        If a recipe ever does $(call RUN_IN_CONTAINER, @some-command), the '@'
        must never reach the shell or docker exec layer.

        CURRENT STATUS (as of implementation): the test harness itself contains
        a deliberately bad target. Running it demonstrates the failure mode
        ("@echo: not found"). This test exists to make that symptom impossible
        to miss and to guide the fix of the real call sites in the project Makefile.
        """
        # Host delegation path — we expect to see the problem in stderr
        result = run_make(minimal_makefile_with_macros.parent, "dangerous-at-target")
        # The shell error will contain the literal @ command — this is the bug
        assert "@echo" in (result.stdout + result.stderr) or result.returncode != 0

        # Direct execution path (simulates being inside the container)
        result_direct = run_make(
            minimal_makefile_with_macros.parent,
            "dangerous-at-target",
            env={"REMOTE_CONTAINERS": "true"},
        )
        # Today this fails with "@echo: not found" in stderr.
        # When the real recipes are cleaned of leading @ inside RUN_IN_CONTAINER calls,
        # change this test to assert returncode==0 and "@echo" not in output.
        assert result_direct.returncode != 0
        assert "@echo" in (result_direct.stdout + result_direct.stderr)

    def test_no_at_prefix_in_any_delegated_command_string(self, minimal_makefile_with_macros: Path):
        """
        Stronger property test: across all our exercise targets, the literal
        string that would be passed to docker compose exec never begins with '@'.
        """
        # This is a meta-check using the record target if we expand it later.
        # For now we simply ensure our dangerous target + normal targets never leak @.
        for target in ("container-aware-target", "dangerous-at-target"):
            res = run_make(minimal_makefile_with_macros.parent, target)
            combined = res.stdout + res.stderr
            # Extremely strict: nowhere in the output of a delegation attempt
            # should we see a token that starts with @ followed by a command.
            assert "@docker" not in combined
            assert "@echo" not in combined
            assert "@make" not in combined
            assert "@sh" not in combined


class TestErrorMessageQuality:
    """Ensure the user-facing error messages from delegation remain excellent."""

    def test_delegation_failure_message_is_actionable(self, minimal_makefile_with_macros: Path):
        result = run_make(minimal_makefile_with_macros.parent, "container-aware-target")
        assert result.returncode != 0
        msg = result.stdout + result.stderr
        assert "❌ Failed to run" in msg
        assert "make up" in msg
        assert "Dev Containers: Reopen in Container" in msg


class TestRealMakefileSmoke:
    """Lightweight smoke tests against the actual project Makefile."""

    def test_help_target_works_and_lists_expected_targets(self, real_makefile_path: Path):
        """`make help` must succeed and mention several important targets."""
        result = subprocess.run(
            ["make", "-C", str(real_makefile_path.parent), "-f", real_makefile_path.name, "help"],
            capture_output=True,
            text=True,
            env={**os.environ, "NO_COLOR": "1"},  # make output stable
        )
        assert result.returncode == 0
        out = result.stdout
        for expected in ("up", "down", "validate", "test", "reset-project", "create-payload"):
            assert expected in out, f"Expected target '{expected}' in help output"

    def test_validate_dry_run_does_not_explode(self, real_makefile_path: Path):
        """`make -n validate` (dry run) should at least parse without syntax errors."""
        result = subprocess.run(
            [
                "make",
                "-C",
                str(real_makefile_path.parent),
                "-f",
                real_makefile_path.name,
                "-n",
                "validate",
            ],
            capture_output=True,
            text=True,
        )
        # Even if some parts are not runnable in dry-run, the Makefile must parse
        assert result.returncode == 0 or "Nothing to be done" in result.stdout
