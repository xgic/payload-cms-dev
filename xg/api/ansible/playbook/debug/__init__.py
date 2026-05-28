"""XG Ansible Playbook Debugger Textual App

This module leverages the power of the Textual RAD framework to accelerate
Ansible testing and debugging by automating repetitive tasks and assisting in
the analysis of playbook results.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Annotated, Any, Dict, List

from pydantic import FilePath, StringConstraints, ValidationError, validate_call
from textual import work
from textual.app import App
from textual.containers import Container, VerticalScroll
from textual.widgets import Static
from textual.worker import Worker, get_current_worker

from xg import util
from xg.api.ansible.constants import Playbook
from xg.api.ansible.playbook import XGPlaybook
from xg.api.ansible.playbook.debug.constants import XGAppConstants
from xg.api.ansible.playbook.debug.hosts import XGPlaybookDebuggerHostsScreen
from xg.api.ansible.playbook.debug.json_results import (
    XGPlaybookDebuggerJsonScreen,
)
from xg.api.ansible.playbook.debug.plays import (
    XGPlaybookDebuggerPlaysScreen,
    XGPlaybookDescription,
    XGPlaybookPlaysDisplay,
)
from xg.api.ansible.playbook.debug.stats import XGPlaybookStatsDisplay
from xg.api.ansible.playbook.debug.tasks import XGPlaybookDebuggerTasksScreen
from xg.api.ansible.playbook.debug.timer import XGTimeDisplay


class XGPlaybookDebugger(App):
    """A Xoren Games application to automate debugging Ansible playbooks in VS
    Code.
    """

    CSS_PATH = "./debug.tcss"

    BINDINGS = [
        ("p", "app.push_screen('plays')", "Plays"),
        ("h", "app.push_screen('hosts')", "Hosts"),
        ("i", "app.push_screen('issues')", "Issues"),
        ("j", "app.push_screen('json')", "JSON"),
        ("t", "app.push_screen('tasks')", "Tasks"),
        ("r", "restart_playbook", "Run"),
        ("q", "quit", "Quit"),
    ]

    @validate_call
    def __init__(self, playbook_filepath: FilePath | None = None):
        super().__init__()
        self.changed_view: bool = False
        self.dark: bool = False
        self.metadata: Dict[str, Any] = {}
        self.playbook_timeout: float = 15

        if not playbook_filepath:
            playbook_filepath = Playbook.PING_ALL_HOSTS

        self.playbook: XGPlaybook = XGPlaybook(
            playbook_filepath=playbook_filepath, debug_mode=False
        )
        self.app_env = os.environ.get("APP_ENV", "")
        self.title = f"{XGAppConstants.APP_NAME} ({self.app_env})"

    async def action_restart_playbook(self) -> None:
        """Called start a new playbook run."""
        self.push_screen("plays")
        self.playbook_stats_container.remove_children()
        self.playbook_plays_container.remove_children()
        self.playbook_main_results_container.loading = True
        self.playbook_timer.reset()
        await self.run_playbook_async()

    async def action_start_stop_xg_timer(self) -> None:
        """Starts or stops the timer."""

        if self.playbook_timer.has_class("started"):
            self.playbook_timer.stop()
            self.playbook_timer.remove_class("started")
        else:
            await self.playbook_timer.start()
            self.playbook_timer.add_class("started")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def validate_playbook_results(self) -> None:
        """Validate Ansible playbook results and create a Pydantic playbook
        results model.
        """
        try:
            self.playbook.validate_results()
        except ValidationError as error:
            raise RuntimeError(
                XGAppConstants.ERROR_CREATING_PYDANTIC_MODEL
            ) from error

    @validate_call
    def get_current_date_time(
        self,
        datetime_format: Annotated[
            str, StringConstraints(min_length=2)
        ] = "%Y-%m-%d %H:%M:%S",
    ) -> str:
        """Gets the current date and time in the specified format.

        Args:
            datetime_format (str, optional): A date time format string with a
            minimal length of 2 characters. Defaults to "%Y-%m-%d %H:%M".

        Returns:
            str: A date and time string in the specified format. Defaults to the
            format yyyy-mm-dd hh:mm:ss (e.g. 2024-01-16 21:31:00) if not
            specified.
        """
        return util.get_current_date_and_time(datetime_format=datetime_format)

    def get_playbook_output(self, gather_facts: bool = True) -> Dict[str, Any]:
        """Gets Ansible playbook output. If an optional input playbook results
        file is provided, it reads the input file instead of running the
        playbook.

        Args:
            gather_facts (bool, optional): If false, disables Ansible fact
            gathering unless it's requested explicitly. Use with caution because
            some playbooks require default fact gathering. Defaults to True.

        Returns:
            Dict[str, Any]: A dictionary containing the process return values of
            return code, stdout and stderr.
        """

        if not self.playbook.results_input_filepath:
            command = ["ansible-playbook", self.playbook.filepath]
            temp_env = None

            if gather_facts is False:
                temp_env = os.environ.copy()
                temp_env["ANSIBLE_GATHERING"] = "explicit"

            output = self.run_command(
                command=command, environment=temp_env, timeout=1200
            )
        else:
            output: Dict[str, Any] = {
                "return_code": 0,
                "stderr": "",
                "stdout": "",
            }

            try:
                output["stdout"] = self.playbook.results_input_filepath.open(
                    mode="r", encoding="utf-8"
                ).read()
            except Exception as error:
                raise RuntimeError(
                    XGAppConstants.ERROR_INPUT_FILE_READ_ERROR
                ) from error

        return output

    def load_playbook_results_json_data(self) -> None:
        """Load Ansible playbook"""
        try:
            self.playbook.results_dict = json.loads(
                self.playbook.output["stdout"]
            )
        except TypeError as error:
            raise RuntimeError(
                XGAppConstants.ERROR_LOADING_JSON_RESULTS
            ) from error

    def on_load(self) -> None:
        """Handles the on load event."""
        now = self.get_current_date_time()
        self.log(f"Starting {self} at {now}.")

    def on_mount(self) -> None:
        """Event handler called when widgets is added to the app."""

        self.install_screen(
            XGPlaybookDebuggerHostsScreen(
                playbook=self.playbook, issues_only=True
            ),
            name="hosts",
        )
        self.install_screen(
            XGPlaybookDebuggerTasksScreen(
                playbook=self.playbook, issues_only=True
            ),
            name="issues",
        )
        self.install_screen(
            XGPlaybookDebuggerJsonScreen(playbook=self.playbook), name="json"
        )
        self.install_screen(
            XGPlaybookDebuggerPlaysScreen(playbook=self.playbook), name="plays"
        )
        self.install_screen(
            XGPlaybookDebuggerTasksScreen(
                playbook=self.playbook, issues_only=False
            ),
            name="tasks",
        )
        self.push_screen("plays")

    async def on_ready(self) -> None:
        """Called  when the DOM is ready."""
        await self.run_playbook_async()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        self.log(event)

    @property
    def playbook_description(self) -> XGPlaybookDescription:
        """Gets the playbook description widget."""
        return self.screen.query_one(
            "#playbook-description", XGPlaybookDescription
        )

    @property
    def playbook_main_results_container(self) -> VerticalScroll:
        """Get the playbook main results container widget."""
        return self.screen.query_one("#main-results-container", VerticalScroll)

    @property
    def playbook_plays_container(self) -> Container:
        """Get the playbook plays container."""
        return self.screen.query_one("#playbook-plays-container", Container)

    @property
    def playbook_results_json(self) -> Static:
        """Get the playbook results static JSON syntax widget."""
        return self.screen.query_one("#results-json", Static)

    @property
    def playbook_stats_container(self) -> Container:
        """Get the playbook stats container."""
        return self.screen.query_one("#playbook-stats-container", Container)

    @property
    def playbook_timer(self) -> XGTimeDisplay:
        """Get the playbook timer widget."""
        return self.screen.query_one("#playbook-timer", XGTimeDisplay)

    @validate_call
    def process_playbook_output(self, playbook_output: Dict[str, Any]) -> None:
        """Process Ansible playbook output.

        Args:
            playbook_output (Dict[str, Any]): A dictionary containing the
            process return values of return code, stdout and stderr.
        """
        self.playbook.output = playbook_output
        self.load_playbook_results_json_data()
        self.validate_playbook_results()
        self.view_playbook_results_main()

    def run_command(
        self,
        command: List[str],
        environment: Dict[str, str] | None = None,
        timeout: float = 15,
    ) -> Dict[str, Any]:
        """Runs a command subprocess using the specified arguments.

        Args:
            command (List[str]): A list of arguments. The first argument must be
            the executable program or command.
            environment (Dict[str, str] | None): If set, the command run with
            the specified environment variables.
            timeout (float): The process timeout in seconds. If the process timeout
            expires a subprocess.TimeoutExpired exception occurs. Defaults to
            15 seconds.

        Raises:
            RuntimeError: If any errors occurred while running the subprocess.

        Returns:
            Dict[str, Any]: A dictionary containing the process return values of
            return code, stdout and stderr.
        """
        # Set output defaults
        stderr: str = ""
        stdout: str = ""
        return_code: Any = None
        output: Dict[str, Any] = {
            "return_code": None,
            "stdout": None,
            "stderr": None,
        }

        # Execute the child program in a new process and store the return
        # values.
        self.log(f"\nStarting subprocess ({locals()})\n")
        with subprocess.Popen(
            command,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as process:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except TimeoutExpired as error:
                process.kill()
                raise RuntimeError(
                    f"TimeoutExpired ({error}) running command {command}, "
                    f"output=[{output}]."
                ) from error
            except OSError as error:
                raise RuntimeError(
                    f"OSError ({error}) running command {command}, output=[{output}]."
                ) from error
            except Exception as error:
                raise RuntimeError(
                    f"Error ({error}) running command {command}, output=[{output}]."
                ) from error
            finally:
                stdout, stderr = process.communicate()
                return_code = process.returncode
                output = {
                    "return_code": return_code,
                    "stderr": stderr,
                    "stdout": stdout,
                }

        return output

    @work(name="run_playbook_worker", thread=True)
    def run_playbook(self) -> None:
        """Runs an Ansible playbook in a new worker thread."""
        self.log("Starting playbook at " f"{self.get_current_date_time()}")

        worker = get_current_worker()
        playbook_output = self.get_playbook_output()

        if not worker.is_cancelled:
            self.call_from_thread(self.process_playbook_output, playbook_output)

    async def run_playbook_async(self) -> None:
        """Runs a playbook asynchronously."""
        self.run_worker(
            work=self.playbook_timer.start(), name="playbook_timer_worker"
        )
        self.run_playbook()

    def view_hidden_widgets(self) -> None:
        """View widgets that were hidden pending data updates."""
        self.playbook_description.remove_class("pending")

    def view_playbook_plays(self) -> None:
        """View playbook plays."""
        plays_container = self.playbook_plays_container
        plays_container.mount(
            XGPlaybookPlaysDisplay(plays=self.playbook.results.plays)
        )

    def view_playbook_results_main(self) -> None:
        """View the current Ansible playbook's results main screen."""
        self.view_playbook_stats()
        self.view_playbook_plays()
        self.view_hidden_widgets()
        self.playbook_timer.stop()
        self.playbook_main_results_container.loading = False

    def view_playbook_stats(self) -> None:
        """View playbook stats."""
        stats_container = self.playbook_stats_container
        stats_container.mount(
            XGPlaybookStatsDisplay(stats=self.playbook.results.stats)
        )


def __add_arguments(parser: argparse.ArgumentParser) -> None:
    """Adds required and optional arguments.

    Args:
        parser (ArgumentParser): An instance of the ArgumentParser class
    """
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help=XGAppConstants.ARGS_JSON,
        required=False,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help=XGAppConstants.ARGS_TIMEOUT,
        required=False,
        type=float,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=XGAppConstants.ARGS_VERBOSE,
        required=False,
    )

    # Mutually exclusive args
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f",
        "--playbook-file",
        help=XGAppConstants.ARGS_PLAYBOOK,
        required=False,
        type=str,
    )
    group.add_argument(
        "-i",
        "--input-file",
        help=XGAppConstants.ARGS_INPUT,
        required=False,
        type=str,
    )


def __get_argument_parser() -> argparse.ArgumentParser:
    """Instantiates the ArgumentParser class.

    Returns:
        (ArgumentParser) An instance of the ArgumentParser class
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog=XGAppConstants.APP_NAME,
        description=XGAppConstants.APP_DESCRIPTION,
        epilog=XGAppConstants.APP_EPILOG,
    )

    __add_arguments(parser)

    return parser


def __process_args() -> bool:
    """Process arguments.

    Raises:
        FileNotFoundError: If an invalid playbook filepath is specified.
        FileNotFoundError: If an invalid playbook results input file is
        specified.
    Returns:
        bool: True if no optional output arguments are specified.
    """
    is_normal_run = False
    args_parser = __get_argument_parser()
    app_args = args_parser.parse_args()

    if app_args.verbose and not app_args.json:
        print(f"\nRunning module {__file__} [sys.argv = {sys.argv}].\n")
        print(app_args)

    # Process optional playbook parameter.
    if app_args.playbook_file:
        playbook_file: Path = Path(app_args.playbook_file)
        if playbook_file.exists():
            app.playbook.filepath = playbook_file
        else:
            raise FileNotFoundError(
                XGAppConstants.ERROR_PLAYBOOK_FILE_NOT_FOUND
            )
    # Process optional input file parameter.
    if app_args.input_file:
        input_file: Path = Path(app_args.input_file)
        if input_file.exists():
            app.playbook.results_input_filepath = input_file
        else:
            raise FileNotFoundError(XGAppConstants.ERROR_INPUT_FILE_NOT_FOUND)

    # Process optional timeout argument
    if app_args.timeout:
        app.playbook_timeout = app_args.timeout

    # Process optional output arguments and run playbook without UI.  The JSON
    # option is required for all automated test that need structured data
    # results.
    if app_args.json:
        # Disable debug mode for test that check for valid JSON in STDOUT.
        app.playbook.debug_mode = False
        app.playbook.output = app.get_playbook_output()

        if app.playbook.output.get("stdout"):
            print(app.playbook.output["stdout"].strip())

    # Run in verbose mode for visual review of output; this mode can't be used
    # for most automated tests because they need JSON structured data.
    elif app_args.verbose:
        app.playbook.debug_mode = True
        app.playbook.output = app.get_playbook_output()
        app.load_playbook_results_json_data()
        app.validate_playbook_results()
    else:
        is_normal_run = True

    return is_normal_run


app: XGPlaybookDebugger = XGPlaybookDebugger()


def main() -> None:
    """Main function of Ansible playbook debug module."""
    # Initialize app
    if __process_args():
        # Run app normally with Textual UI, if no optional output arguments are
        # specified. The UI will cause automated tests to fail with timeout errors.
        subprocess.call("reset")
        try:
            app.run()
        except RuntimeError as _error:
            print("A runtime error occurred.\n" f"{util.inspect(_error)}")
            sys.exit(2)
