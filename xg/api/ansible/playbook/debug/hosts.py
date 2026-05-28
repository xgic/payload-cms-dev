"""XG Ansible Playbook Debugger Hosts Module"""

from typing import List

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from xg.api.ansible.playbook import (
    XGAnsiblePlay,
    XGPlaybook,
    XGPlaybookHostTaskResult,
    XGPlaybookTask,
    XGStatus,
)


class XGPlaybookDebuggerHostsScreen(Screen):
    """A screen to show playbook hosts results and debugging information."""

    DEFAULT_CSS = """
    XGPlaybookDebuggerHostsScreen {
        color: $text;
        height: auto;
        layout: vertical;
        width: 100%;
        .task-headers {
            background: $primary-lighten-2;
            content-align: left middle;
            grid-columns: 1fr 13 13 13 13 13 13 2;
            grid-size: 8;            
            layout: grid;
            padding: 0 1;
        }
    }
    """

    BINDINGS = []

    def __init__(
        self,
        playbook: XGPlaybook,
        issues_only: bool = False,
        name: str | None = None,
        screen_id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.playbook = playbook
        self.issues_only = issues_only
        super().__init__(name, screen_id, classes)

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        yield Footer()
        with Static(classes="task-headers"):
            yield Static("host")
            yield Static("changed")
            yield Static("failed")
            yield Static("ignored")
            yield Static("rescued")
            yield Static("skipped")
            yield Static("unreachable")
        with VerticalScroll(id="play-container"):
            yield XGPlaybookTaskDisplay(
                plays=self.playbook.results.plays, issues_only=self.issues_only
            )


class XGPlaybookHostTaskResultDisplay(Static):
    """An Ansible playbook host task result display widget."""

    DEFAULT_CSS = """
    XGPlaybookHostTaskResultDisplay {
        color: $text;
        height: auto;
        layout: vertical;
        width: 100%;
        .error {
            color: $error
        }
        .host {
            &:hover {
                background: $primary-background-lighten-1 40%;
            }
        }
        .host-container {
            content-align: left middle;
            grid-columns: 1fr 13 13 13 13 13 13;
            grid-size: 7;
            layout: grid;
            padding: 0 1;
        }
        .message {
            padding: 0 1;
        }
        .success {
            color: $success-darken-3
        }
        .warning {
            color: $warning-lighten-2
        }
    }
    """

    def __init__(
        self, playbook_task: XGPlaybookTask, issues_only: bool = False
    ) -> None:
        self.playbook_task = playbook_task
        self.issues_only = issues_only
        super().__init__()

    def compose(self) -> ComposeResult:
        with Static(classes="hosts"):
            for host in self.playbook_task.hosts:
                host_result: XGPlaybookHostTaskResult = (
                    self.playbook_task.hosts[host]
                )
                if self.issues_only and host_result.status == XGStatus.SUCCESS:
                    continue
                with Static(
                    classes=f"host-container {host_result.status.value}"
                ):
                    yield Static(f"{host}", classes="host")
                    yield Static(f"{host_result.changed}", classes="host")
                    yield Static(f"{host_result.failed}", classes="host")
                    yield Static(f"{host_result.ignored}", classes="host")
                    yield Static(f"{host_result.rescued}", classes="host")
                    yield Static(f"{host_result.skipped}", classes="host")
                    yield Static(f"{host_result.unreachable}", classes="host")
                if host_result.task_data.get("msg"):
                    yield Static(
                        f"\nMessage:\n{host_result.task_data['msg']}",
                        classes=f"message {host_result.status.value}",
                    )
                if host_result.warnings:
                    yield Static(
                        "\nWarnings:",
                        classes=f"message {host_result.status.value}",
                    )
                    for warning in host_result.warnings:
                        yield Static(
                            f"{warning}",
                            classes=f"message {host_result.status.value}",
                        )
        return super().compose()


class XGPlaybookTaskDisplay(Static):
    """An Ansible playbook task display widget."""

    DEFAULT_CSS = """
    XGPlaybookTaskDisplay {
        color: $text;
        height: auto;
        layout: vertical;
        width: 100%;
        .error {
            color: $error
        }
        .play {
            background: $primary-background;
            content-align: center middle;
            margin: 0;
            padding: 0 1;
            text-style: bold;
            width: 100%;
        }
        .success {
            color: $success-darken-3
        }
        .task {
            background: $boost;
            content-align: center middle;
            padding: 0 1;
            width: 100%;
        }
        .warning {
            color: $warning-lighten-2
        }
    }
    """

    def __init__(
        self, plays: List[XGAnsiblePlay], issues_only: bool = False
    ) -> None:
        self.plays = plays
        self.issues_only = issues_only
        super().__init__()

    def compose(self) -> ComposeResult:
        for play in self.plays:
            if self.issues_only and play.status == XGStatus.SUCCESS:
                continue
            yield Static(play.play.name, classes=f"play {play.status.value}")
            for task in play.tasks:
                if self.issues_only and task.status == XGStatus.SUCCESS:
                    continue
                yield Static(
                    task.task.name, classes=f"task {task.status.value}"
                )
                yield XGPlaybookHostTaskResultDisplay(
                    playbook_task=task, issues_only=self.issues_only
                )

        return super().compose()
