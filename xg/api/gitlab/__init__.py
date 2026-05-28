"""XG GitLab API Module

This module enables using the REST and GraphQL APIs.
"""
import requests


class RestAPI:
    """This class enables using the GitLab REST API on our internal Xoren Games
    GitLab server.
    """

    def __init__(self) -> None:
        """Initialize the class."""
        self.xg_gitlab_url: str = "https://gitlab.xorengames.com"

    def create_project(self) -> None:
        """Creates a project in GitLab."""
        print("Creating XG GitLab project.")

    # curl --request GET "https://gitlab.example.com/api/v4/projects"
    # curl "https://gitlab.example.com/api/v4/projects? \
    #   private_token=<your_access_token>"
    # curl --header "Authorization: Bearer <your_access_token>" \
    #   "https://gitlab.example.com/api/v4/projects"
    def get_all_projects(self, access_token: str) -> None:
        """Get all project data accessible with the provided API access token.

        Args:
            access_token (str): GitLab API access token.
        """
        uri: str = f"{self.xg_gitlab_url}/api/v4/projects"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(uri, headers=headers, timeout=60)
        print(response)
