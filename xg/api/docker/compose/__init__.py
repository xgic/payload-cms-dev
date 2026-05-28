"""XG Docker Compose API Module

This module defines an API for the Docker Compose V2 console application.
"""

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from xg import util


class Project(BaseModel):
    """A class to store information about a Docker Compose project.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic base model.
    """

    Name: str
    """The name of the Docker Compose project."""
    Status: str
    """The current status of the project (e.g., 'running', 'exited')."""
    ConfigFiles: str
    """The path(s) to the configuration file(s) used by the project."""


def get_running_projects() -> list[Project]:
    """Gets a list of all running Docker Compose projects.

    This function executes 'docker compose ls --format json', parses the output,
    creates Project instances for each project, and returns those with status
    'running'.


    Returns:
        list[Project]: A list of Project instances representing running
        projects.
    """
    # Execute the docker compose command and capture the output
    args: List[str] = ["docker", "compose", "ls", "--format", "json"]
    output: Dict[str, Any] = util.run_command(args=args)

    # Parse the JSON output into a Python list of dictionaries
    projects_data = json.loads(output["stdout"])

    # Convert each project dictionary into a Project instance
    all_projects = [Project(**project) for project in projects_data]

    # Filter to include only projects with status 'running' (case-insensitive)
    return [
        project
        for project in all_projects
        if project.Status.lower().startswith("running")
    ]


def get_running_project_names(starts_with: Optional[str] = None) -> list[str]:
    """
    Gets a list of running Docker Compose project names, optionally filtered by
    a 'starts with' condition.

    Args:
        starts_with (Optional[str]): If provided, only return project names
        that start with this string. If None or an empty string, all running
        project names are returned.

    Returns:
        list[str]: A list of running project names, filtered if 'starts_with'
        is specified.
    """
    running_projects = get_running_projects()
    return [
        project.Name
        for project in running_projects
        if starts_with is None or project.Name.startswith(starts_with)
    ]


# # Optionally update the in-memory collection when the module is loaded
# try:
#     projects = get_running_projects()
#     # print(projects)
# except RuntimeError as e:
#     print(f"Failed to initialize running_projects: {e}")
