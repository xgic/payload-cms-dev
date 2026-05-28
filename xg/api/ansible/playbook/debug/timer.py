"""XG Timer Module"""

from time import monotonic
from typing import Any

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Button, Static

from xg import util


class XGTimeDisplay(Static):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)
    update_timer: Any

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(0.1, self.update_time, pause=True)

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0

    async def start(self) -> None:
        """Method to start (or resume) time updating."""
        current_datetime = util.get_current_date_and_time()
        message = f"Starting timer at {current_datetime}"
        self.log(message)
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = self.total + monotonic() - self.start_time

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")


class XGTimer(Static):
    "A timer widget."

    def compose(self) -> ComposeResult:
        """Create child widgets of the timer."""
        yield XGTimeDisplay(id="time-display")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(XGTimeDisplay)
        if button_id == "start":
            await time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()


class XGPlaybookTimer(Static):
    """A widget to display a timer for the current playbook."""

    DEFAULT_CSS = """
    XGPlaybookTimer {
        height: 1;
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield XGTimer()

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
