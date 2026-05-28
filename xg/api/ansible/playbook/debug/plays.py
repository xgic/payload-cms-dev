"""XG Ansible Playbook Debugger Plays Module"""

from typing import List

from pydantic import UUID4
from textual.app import ComposeResult, RenderResult
from textual.containers import Container, VerticalScroll
from textual.events import Mount
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from xg.api.ansible.playbook import (
    XGAnsiblePlay,
    XGPlaybook,
    XGPlaybookPlayDetails,
)
from xg.api.ansible.playbook.debug.timer import XGTimeDisplay


class XGPlaybookInformation(Container):
    """A container for main Ansible playbook information.

    The main playbook is specified in the Ansible playbook command.
    """

    def __init__(self, playbook: XGPlaybook, widget_id: str) -> None:
        self.playbook: XGPlaybook = playbook
        super().__init__(id=widget_id)

    def compose(self) -> ComposeResult:
        yield XGPlaybookPathMain(
            playbook=self.playbook,
            widget_id="playbook-path",
        )
        yield XGPlaybookDescription(
            playbook=self.playbook,
            widget_id="playbook-description",
        )
        yield XGTimeDisplay(id="playbook-timer")
        return super().compose()


class XGPlaybookDescription(Static):
    """A widget to display Ansible playbook short description."""

    def __init__(self, playbook: XGPlaybook, widget_id: str) -> None:
        self.playbook: XGPlaybook = playbook
        super().__init__(id=widget_id)

    def render(self) -> RenderResult:
        return f"[b]Description: {self.playbook.description}[/b]"

    def _on_mount(self, event: Mount) -> None:
        self.add_class("pending")

        return super()._on_mount(event)


class XGPlaybookPathMain(Static):
    """A widget to display Ansible main playbook path."""

    def __init__(self, playbook: XGPlaybook, widget_id: str) -> None:
        self.playbook: XGPlaybook = playbook
        super().__init__(id=widget_id)

    def render(self) -> RenderResult:
        heading: str
        if not self.playbook.results_input_filepath:
            heading = f"[b]Main Playbook: {self.playbook.filepath}[/b]"
        else:
            heading = (
                f"[b]Input File: {self.playbook.results_input_filepath}[/b]"
            )

        return heading


class XGPlaybookPlayDisplayHeader(Static):
    """An Ansible playbook play display header widget."""

    DEFAULT_CSS = """
    XGPlaybookPlayDisplayHeader {
        background: $boost;
        height: 1;
        .play-header {
            content-align: center middle;
            margin: 0;
            padding: 0 1;
            text-style: bold;
            width: 100%;
            &:hover {
                background: $primary-background-lighten-1 40%;
            }
        }
        .play-header-selected {
            content-align: left middle;
            height: 1;
            margin: 0;
            padding: 0;
        }
        .play-header-container {
            content-align: left middle;
            grid-columns: 6 1fr 6;
            grid-size: 3;
            layout: grid;
            margin: 0;
            padding: 0 1;
        }
    }
    """

    header: str
    selected: reactive[bool] = reactive(False)
    status: str
    play_id: UUID4

    def __init__(
        self,
        header: str,
        play_id: UUID4,
        status: str,
        classes: str | None = None,
    ) -> None:
        self.header = header
        self.play_id = play_id
        self.status = status
        super().__init__(classes=classes)

    def on_click(self) -> None:
        """On click event handler for the XG playbook play display header
        widget.
        """
        selected_value: str
        self.selected = not self.selected

        if self.selected:
            selected_value = (
                f"[{self.status}]:heavy_check_mark:[/{self.status}] "
                f"{self.header}"
            )
        else:
            selected_value = self.header

        self.query_one("#play-header", Static).update(selected_value)

    def compose(self) -> ComposeResult:
        yield Static(f"{self.header}", id="play-header", classes="play-header")


class XGPlaybookPlayDisplay(Static):
    """An Ansible playbook play display widget."""

    DEFAULT_CSS = """
    XGPlaybookPlayDisplay {
        color: $text-muted;
        height: 2;
        layout: grid;
        margin: 0;
        width: 100%;
        .count {
            content-align: right middle;
            margin: 0;
            padding: 0 1;
        }
        .error {
            color: $error
        }
        .label {
            content-align: left middle;
            margin: 0;
            padding: 0 1;
        }
        .path {
            content-align: left middle;
            margin: 0;
            padding: 0 1;
        }
        .play-container {
            content-align: left middle;
            grid-columns: auto 1fr auto auto auto auto;
            grid-size: 6;
            layout: grid;
            margin: 0;
            padding: 0 1;
        }
        .selected {
            background: $primary;
        }
        .success {
            color: $success-darken-3
        }
        .warning {
            color: $warning-lighten-2
        }
    }
    """
    play: XGAnsiblePlay

    def __init__(self, play: XGAnsiblePlay) -> None:
        self.play = play
        super().__init__()

    def compose(self) -> ComposeResult:
        play_details: XGPlaybookPlayDetails = self.play.play
        play_status: str = self.play.status.value

        yield XGPlaybookPlayDisplayHeader(
            header=play_details.name,
            play_id=play_details.id,
            status=play_status,
            classes=f"play-header {play_status}",
        )
        with Static(classes=f"play-container {play_status}"):
            yield Static("Path:", classes="label")
            yield Static(f"{play_details.path}", classes="path")

            yield Static("Tasks:", classes="label")
            yield Static(f"{self.play.task_count}", classes="count")

            yield Static("Issues:", classes="label")
            yield Static(f"{self.play.issues_count}", classes="count")

        return super().compose()


class XGPlaybookPlaysDisplay(Static):
    """An Ansible playbook plays display widget."""

    DEFAULT_CSS = """
    XGPlaybookPlaysDisplay {
        color: $text;
        height: auto;
        layout: vertical;
        margin: 0;
        padding: 0;
        text-style: bold;
        width: 100%;
        .heading {
            margin: 0;
            padding: 0;
            background: $primary-background;
            content-align: center middle;
            width: 100%
        }
    }
    """
    plays: List[XGAnsiblePlay] = []

    def __init__(self, plays: List[XGAnsiblePlay]) -> None:
        self.plays = plays
        super().__init__()

    def compose(self) -> ComposeResult:
        if len(self.plays) > 0:
            yield Static("Ansible Playbook Plays", classes="heading")
            for play in self.plays:
                yield XGPlaybookPlayDisplay(play=play)

        return super().compose()


class XGPlaybookDebuggerPlaysScreen(Screen):
    """A screen to show playbook output and debugging information."""

    BINDINGS = []

    def __init__(
        self,
        playbook: XGPlaybook,
        name: str | None = None,
        screen_id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.playbook = playbook
        super().__init__(name, screen_id, classes)

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header()
        yield Footer()
        yield XGPlaybookInformation(
            widget_id="playbook-information", playbook=self.playbook
        )
        with VerticalScroll(id="main-results-container"):
            yield Container(id="playbook-stats-container")
            yield Container(id="playbook-plays-container")

    def _on_mount(self, event: Mount) -> None:
        main_container = self.query_one(
            "#main-results-container", VerticalScroll
        )
        main_container.loading = True
        return super()._on_mount(event)
