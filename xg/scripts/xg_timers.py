"""The XG Timers application integrates with XG AIS and XG CMS to provide
automated time tracking data entry.
"""
from time import monotonic
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static


class TimeDisplay(Static):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def __init__(self):
        super().__init__()
        self.update_timer: Any

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(0.1, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = self.total + monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0


class XGTimer(Static):
    "A timer widget."

    def compose(self) -> ComposeResult:
        """Create child widgets of the timer."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()


class XGTimers(App):
    """A Xoren Games application to automate accurate time tracking.

    Features:
    - Voice recognition for managing the creation, starting and stop timers as
    well as keyboard and mouse support.
    - AI assisted data entry into time management systems including optional
    integrations to GitLab
    """

    CSS_PATH = "../.css/xg_timers_00.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_xg_timer", "Add"),
        ("r", "remove_xg_timer", "Remove"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(XGTimer(), XGTimer(), XGTimer(), id="timers")

    def action_add_xg_timer(self) -> None:
        """An action to add a timer."""
        new_xg_timer = XGTimer()
        self.query_one("#timers").mount(new_xg_timer)
        new_xg_timer.scroll_visible()

    def action_remove_xg_timer(self) -> None:
        """Called to remove a timer."""
        timers = self.query("XGTimer")
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = XGTimers()
    app.run()
