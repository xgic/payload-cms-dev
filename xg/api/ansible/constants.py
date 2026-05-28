"""Xoren Games Ansible API constants module."""

from typing import ClassVar

from pydantic import BaseModel, FilePath

from xg import util


class Playbook(BaseModel):
    """Ansible playbook path data.

    Args:
        BaseModel (pydantic.BaseModel): Inherits from Pydantic BaseModel class.
    """

    PING_ALL_HOSTS: ClassVar[FilePath] = util.ANSIBLE_DIR.joinpath("test.yml")
    PING_CONTROL_NODES: ClassVar[FilePath] = util.ANSIBLE_DIR.joinpath(
        "playbooks/test_control_node.yml"
    )
