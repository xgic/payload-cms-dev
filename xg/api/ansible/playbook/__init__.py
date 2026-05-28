"""Xoren Games Ansible API module."""

import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pydantic import UUID4, BaseModel, FilePath, NonNegativeInt, StrictStr

from xg import util
from xg.util import XGDuration, XGStatus


class XGTableData(BaseModel):
    """A table data model.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    columns: Tuple[str, ...]
    rows: List[Tuple[Any, ...]]


class XGPlaybookHostStats(BaseModel):
    """An Ansible playbook host results class for processing and validation.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    changed: NonNegativeInt
    failures: NonNegativeInt
    ignored: NonNegativeInt
    ok: NonNegativeInt
    rescued: NonNegativeInt
    skipped: NonNegativeInt
    unreachable: NonNegativeInt

    @property
    def status(self) -> XGStatus:
        """Gets the playbook status of a host.

        Returns:
            XGStatus: A status for the playbook
        """
        host_status: XGStatus
        if self.failures > 0:
            host_status = XGStatus.ERROR
        elif self.unreachable > 0:
            host_status = XGStatus.ERROR
        elif self.ok > 0:
            host_status = XGStatus.SUCCESS
        else:
            host_status = XGStatus.WARNING

        return host_status


class XGPlaybookHostTaskResult(BaseModel):
    """An Ansible playbook host task results class for processing and
    validation.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    # hostname: StrictStr
    action: StrictStr
    ansible_facts: dict | None
    changed: bool | None
    failed: bool | None
    ignored: bool | None
    rescued: bool | None
    skipped: bool | None
    unreachable: bool | None
    warnings: list | None
    task_data: dict

    @property
    def status(self) -> XGStatus:
        """Gets the playbook status of a host.

        Returns:
            XGStatus: A status for the playbook
        """
        host_status: XGStatus
        if self.failed:
            host_status = XGStatus.ERROR
        elif self.unreachable:
            host_status = XGStatus.ERROR
        elif self.warnings and len(self.warnings) > 0:
            host_status = XGStatus.WARNING
        else:
            host_status = XGStatus.SUCCESS

        return host_status


class XGPlaybookPlayDetails(BaseModel):
    """An Ansible playbook play details class for processing and validation.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    id: UUID4
    duration: XGDuration
    name: StrictStr
    path: StrictStr


class XGPlaybookTaskDetails(BaseModel):
    """An Ansible playbook task details class for processing and validation.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    id: UUID4
    duration: XGDuration
    name: StrictStr
    path: StrictStr


class XGPlaybookTask(BaseModel):
    """An Ansible playbook task class for processing and validation.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    hosts: Dict[str, XGPlaybookHostTaskResult]
    task: XGPlaybookTaskDetails

    @property
    def status(self) -> XGStatus:
        """Gets the playbook play status.

        Returns:
            XGStatus: A status for the playbook play.
        """
        play_status: XGStatus = XGStatus.SUCCESS

        for host in self.hosts:
            if self.hosts[host].failed or self.hosts[host].unreachable:
                play_status = XGStatus.ERROR
                break

            warnings_list: list | None = self.hosts[host].warnings
            if isinstance(warnings_list, list) and len(warnings_list) > 0:
                play_status = XGStatus.WARNING

        return play_status


class XGAnsiblePlay(BaseModel):
    """An Ansible playbook play class for processing and validation.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    play: XGPlaybookPlayDetails
    tasks: List[XGPlaybookTask]

    @property
    def error_count(self) -> int:
        """Gets the number of errors in the Ansible playbook play.

        Returns:
            int: An integer indicating the number of errors.
        """
        errors: int = 0

        for task in self.tasks:
            for host in task.hosts:
                if task.hosts[host].failed:
                    errors += 1
                elif task.hosts[host].unreachable:
                    errors += 1

        return errors

    @property
    def issues_count(self) -> int:
        """Gets the number of issues in the Ansible playbook play.

        Returns:
            int: An integer indicating the number of issues.
        """
        return self.error_count + self.warning_count

    @property
    def status(self) -> XGStatus:
        """Gets the playbook play status.

        Returns:
            XGStatus: A status for the playbook play.
        """
        play_status: XGStatus
        if self.error_count > 0:
            play_status = XGStatus.ERROR
        elif self.warning_count > 0:
            play_status = XGStatus.WARNING
        else:
            play_status = XGStatus.SUCCESS
        return play_status

    @property
    def task_count(self) -> int:
        """Gets the number of tasks in the Ansible playbook play.

        Returns:
            int: An integer indicating the number of tasks.
        """

        tasks: int = 0

        for task in self.tasks:
            if isinstance(task, XGPlaybookTask):
                tasks += 1

        return tasks

    @property
    def warning_count(self) -> int:
        """Gets the number of warnings in the Ansible playbook play.

        Returns:
            int: An integer indicating the number of warnings.
        """
        warnings: int = 0

        for task in self.tasks:
            for host in task.hosts:
                warnings_list: list | None = task.hosts[host].warnings

                if warnings_list and isinstance(warnings_list, list):
                    warnings += len(warnings_list)

        return warnings


class XGPlaybookStats(BaseModel):
    """An Ansible playbook stats class for processing and validation.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    hosts: Dict[str, XGPlaybookHostStats]


class XGPlaybookResults(BaseModel):
    """An Ansible playbook results class for processing and validation.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    custom_stats: Dict[str, Any]
    global_custom_stats: Dict[str, Any]
    plays: List[XGAnsiblePlay]
    stats: XGPlaybookStats


class XGPlaybook:
    """An Ansible playbook class for data processing, results validation and
    automated analysis."""

    def __init__(
        self,
        playbook_filepath: Path,
        results_input_filepath: Path | None = None,
        debug_mode: bool = False,
    ) -> None:
        self.debug_mode: bool = debug_mode
        self.output: Dict[str, Any]
        self.filepath: FilePath = playbook_filepath
        self.results: XGPlaybookResults
        self.results_dict: Dict[str, Any]
        self.results_input_filepath: Path | None = results_input_filepath
        self.description: str = ""

    def get_host_task_results(
        self, task_results: Dict[str, Any]
    ) -> Dict[str, XGPlaybookHostTaskResult]:
        """Gets the Ansible playbook host task results dictionary.

        Args:
            task_results (Dict[str, Any]): A dictionary containing the playbook
            tasks results for each host.

        Returns:
            Dict[str, XGPlaybookHostTaskResult]: A dictionary of host task
            result models.
        """
        results: Dict[str, XGPlaybookHostTaskResult] = {}

        for host in task_results:
            results[host] = XGPlaybookHostTaskResult(
                action=task_results[host]["action"],
                ansible_facts=task_results[host].get("ansible_facts"),
                changed=task_results[host].get("changed"),
                failed=task_results[host].get("failed"),
                ignored=task_results[host].get("ignored"),
                rescued=task_results[host].get("rescued"),
                skipped=task_results[host].get("skipped"),
                unreachable=task_results[host].get("unreachable"),
                warnings=task_results[host].get("warnings"),
                task_data=task_results[host],
            )

        return results

    def get_play(self, play: Dict[str, Any]) -> XGPlaybookPlayDetails:
        """Gets the Ansible playbook play details model.

        Returns:
            List[XGAnsiblePlay]: A list of Ansible playbook play models.
        """
        return XGPlaybookPlayDetails(
            id=uuid.UUID(play["id"], version=4),
            duration=XGDuration.model_validate(play["duration"]),
            name=play["name"],
            path=play["path"],
        )

    def get_plays(self) -> List[XGAnsiblePlay]:
        """Gets the Ansible playbook plays model list.

        Returns:
            List[XGAnsiblePlay]: A list of Ansible playbook play models.
        """
        plays_list: List[Dict[str, Any]] = self.results_dict["plays"]
        plays: List[XGAnsiblePlay] = []
        play_count: int = 0

        for play in plays_list:
            if play_count == 0:
                self.description = play["play"]["name"]

            plays.append(
                XGAnsiblePlay(
                    play=self.get_play(play["play"]),
                    tasks=self.get_tasks(play["tasks"]),
                )
            )

            play_count += 1

        return plays

    def get_task(self, task: Dict[str, Any]) -> XGPlaybookTaskDetails:
        """Gets the Ansible playbook task details model.

        Returns:
            List[XGAnsiblePlay]: An Ansible playbook task details model.
        """
        return XGPlaybookTaskDetails(
            id=uuid.UUID(task["id"], version=4),
            duration=XGDuration.model_validate(task["duration"]),
            name=task["name"],
            path=task["path"],
        )

    def get_tasks(self, tasks: List[Dict[str, Any]]) -> List[XGPlaybookTask]:
        """Gets the Ansible playbook task model list.

        Returns:
            List[XGAnsiblePlay]: A list of Ansible task models.
        """
        task_list: List[Dict[str, Any]] = tasks
        task_models: List[XGPlaybookTask] = []

        for task in task_list:
            task_models.append(
                XGPlaybookTask(
                    hosts=self.get_host_task_results(task["hosts"]),
                    task=self.get_task(task["task"]),
                )
            )

        return task_models

    def validate_results(self) -> None:
        """Validate Ansible playbook results."""

        self.results = XGPlaybookResults(
            custom_stats=self.results_dict["custom_stats"],
            global_custom_stats=self.results_dict["global_custom_stats"],
            plays=self.get_plays(),
            stats=XGPlaybookStats(hosts=self.results_dict["stats"]),
        )

        if self.debug_mode:
            util.inspect(self)
