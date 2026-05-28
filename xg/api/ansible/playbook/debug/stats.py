"""XG Ansible Playbook Debugger Stats Module"""

from typing import List

from textual.app import ComposeResult
from textual.widgets import Static

from xg.api.ansible.playbook import XGPlaybookHostStats, XGPlaybookStats


class XGPlaybookStatsDisplayHeaders(Static):
    "An Ansible playbook stats headers display widget."
    DEFAULT_CSS = """
    XGPlaybookStatsDisplayHeaders {
        background: $boost;
        color: $text-muted;
        height: auto;
        width: 100%;
        layout: horizontal;
        .hosts {
            content-align: left middle;
            padding: 0 1;
            width: 35;
        }
        .side-margin {
            width: 1fr
        }
        .stat {
            content-align: left middle;
            width: 14
        }
    }
    """

    def compose(self) -> ComposeResult:
        headers: List[str] = []
        yield Static(classes="side-margin")
        yield Static("host", classes="hosts")
        headers.extend(sorted(XGPlaybookHostStats.model_fields))
        for header in headers:
            yield Static(header, classes="stat")
        yield Static(classes="side-margin")

        return super().compose()


class XGPlaybookStatsDisplayHosts(Static):
    "An Ansible playbook host stats display widget."
    DEFAULT_CSS = """
    XGPlaybookStatsDisplayHosts {
        color: $text;
        height: auto;
        width: 100%;
        layout: horizontal;            
        .error {
            color: $error
        }
        .hosts {
            content-align: left middle;
            padding: 0 1;
            width: 35;
        }
        .side-margin {
            width: 1fr
        }
        .stat {
            content-align: left middle;
            width: 14
        }
        .success {
            color: $success-darken-3
        }
        .warning {
            color: $warning-lighten-2
        }
    }
    """

    host: str
    stats: XGPlaybookHostStats

    def __init__(self, host: str, stats: XGPlaybookHostStats) -> None:
        self.host = host
        self.stats = stats
        super().__init__()

    def compose(self) -> ComposeResult:
        if isinstance(self.stats, XGPlaybookHostStats):
            yield Static(classes="side-margin")
            yield Static(self.host, classes=f"hosts {self.stats.status.value}")
            for stat in self.stats:
                _, value = stat
                yield Static(
                    f"{value}",
                    classes=f"stat {self.stats.status.value}",
                )
            yield Static(classes="side-margin")

        return super().compose()


class XGPlaybookStatsDisplay(Static):
    "An Ansible playbook stats display widget."
    DEFAULT_CSS = """
    XGPlaybookStatsDisplay {
        color: $text;
        height: auto;
        layout: vertical;
        padding: 0;
        width: 100%;
        .error {
            color: $error
        }
        .heading {
            padding: 0;
            background: $primary-background;
            content-align: center middle;
            text-style: bold;
            width: 100%
        }
        .success {
            color: $success-darken-3
        }
        .warning {
            color: $warning-lighten-2
        }
    }
    """

    stats: XGPlaybookStats | None

    def __init__(self, stats: XGPlaybookStats) -> None:
        self.stats = stats
        super().__init__()

    def compose(self) -> ComposeResult:
        if isinstance(self.stats, XGPlaybookStats):
            yield Static("Playbook Stats by Host", classes="heading")
            yield XGPlaybookStatsDisplayHeaders()
            for host in self.stats.hosts:
                yield XGPlaybookStatsDisplayHosts(
                    host=host, stats=self.stats.hosts[host]
                )
        return super().compose()
