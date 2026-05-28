"""XG Ansible Playbook Debugger JSON Results Module"""

from rich.syntax import Syntax
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from xg.api.ansible.playbook import XGPlaybook


class XGPlaybookDebuggerJsonScreen(Screen):
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
        with VerticalScroll(id="json-results-container"):
            yield Static(id="results-json", expand=True)

    def _on_screen_resume(self) -> None:
        self.view_playbook_results_json()
        return super()._on_screen_resume()

    @property
    def playbook_results_json(self) -> Static:
        """Get the playbook results static JSON syntax widget."""
        return self.query_one("#results-json", Static)

    def view_playbook_results_json(self) -> None:
        """View the current Ansible playbook's output using the JSON syntax
        widget.
        """
        syntax = Syntax(
            str(self.playbook.output["stdout"]),
            lexer="json",
            line_numbers=True,
            word_wrap=True,
            indent_guides=True,
            theme="github-dark",
        )
        self.playbook_results_json.update(syntax)
