"""Common part of all `commands` that oGen can execute"""

import os
import click

from .base_config import BaseConfig
from ..project import Project
from ...constants import APP_NAME
from ...exceptions import \
    UserAbortError, \
    ConfigError


class BaseCommand(BaseConfig):
    """Abstract class inherited by all commands of oGen"""

    mode: str
    project: Project

    def __init__(self) -> None:
        # Init config
        app_path = click.get_app_dir(APP_NAME)

        self._config_path = app_path
        self._config_file = 'ogen.conf'
        self._config_header = f'# This is the configuration file for oGen{os.linesep}' \
            f'# Do not change this file manually{os.linesep}{os.linesep}'

        super().__init__()

    def get_default_config(self) -> dict:
        workspace_dir = os.getcwd()
        click.echo(
            f'The following will be your workspace directory: {workspace_dir}')

        # Get user's confirmation to use current path as workspace folder
        cont = click.confirm('Continue?', default=True)
        if not cont:
            important = click.style('Important!', fg='red')
            raise UserAbortError(f'{important} Execute the `ogen` command in the '
                                 'folder that will be your workspace.')

        return {
            'DEFAULT': {
                'workspace_dir': workspace_dir,
                'active_project': ''
            }
        }

    @property
    def conf_dir(self) -> str:
        """
        Gets the path to the config folder.

        Returns:
            str: The path.
        """
        return self._config_path

    def _determine_project(self, project_name: str = ''):
        """
        Initiates the project from arg or from config
        and assigns it to self.project

        Args:
            project_name (str, optional): Desired project name.
                                          Defaults to ''.

        Raises:
            ConfigError: When no argument is passed
                         and no active project found in config.
        """
        project_name = project_name or self.get_config('active_project')
        if not project_name:
            raise ConfigError(
                f'No `active_project` found in {self._config_file_path}')

        self.project = Project(
            command=self,
            project_data={
                'project_name': project_name
            })

    @staticmethod
    def init(gen) -> None:
        """
        Abstract definition for the `init` function.
        It is responsible for attaching the command to the oGen.

        Argument:
            gen: The `gen` group function.

        Raises:
            NotImplementedError: This should never be reached
        """
        raise NotImplementedError()
