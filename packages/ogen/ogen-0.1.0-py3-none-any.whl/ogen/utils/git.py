"""
Git specific functionality
"""

import subprocess
from typing import Union
import click

from ..exceptions import ConfigError
from .helper import execute_command


class GitUtils:  # pylint: disable=too-few-public-methods
    """
    Git specific functions
    """
    repo: Union[str, None]
    branch: Union[str, None]
    shallow: bool

    def __init__(self,
                 repo: Union[str, None] = None,
                 branch: Union[str, None] = None,
                 shallow: bool = False):
        self.repo = repo
        self.branch = branch
        self.shallow = shallow

    @staticmethod
    def check_git_available() -> None:
        """
        Checks if `git` is installed and can be executed.

        Raises:
            ConfigError: Raised when git is not available.
        """
        with subprocess.Popen(
                ["git", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE) as git_check:

            if not git_check.stdout.read().decode("utf-8").strip().startswith('git version'):
                raise ConfigError(
                    "Git is not installed. Please install Git and try again.")

    def clone(self, path: str) -> None:
        """
        Clones Odoo repository

        Args:
            path (str): Destination path
        """
        self.check_git_available()

        click.echo("Cloning repository...")

        command = ['git', 'clone', '--verbose']
        if self.branch:
            command += ['--branch', self.branch]
        if self.shallow:
            command += ['--single-branch', '--depth', '1']
        command += ['--', self.repo, path]

        execute_command(command=command)

        click.echo("Repository cloned successfully!")
