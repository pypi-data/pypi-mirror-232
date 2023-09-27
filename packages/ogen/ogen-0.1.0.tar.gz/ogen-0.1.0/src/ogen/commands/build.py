"""Dedicated space for build commands."""

import click

from ..models.abstract.base_command import BaseCommand
from ..exceptions import handle_error


class BuildCommand(BaseCommand):
    """
    Class that handles specific commands of building a project activity.
    """

    mode: str = 'build'

    @handle_error
    def __init__(self, project_name: str = ''):
        super().__init__()

        self._determine_project(project_name=project_name)

    @handle_error
    def build(self) -> None:
        """
        Function called to execute the `build` command
        """
        self.project.build()
        self.save_config()

    @staticmethod
    def init(gen) -> None:
        """
        Attaches the `build` command to the Generator.

        Argument:
            gen: The `gen` group function.
        """

        @gen.command(help='Builds or rebuilds the docker image for the active project or the one passed as argument')
        @click.argument('project_name', required=False)
        def build(project_name: str = '') -> None:
            """
            Entrypoint for the project `build` command.

            Args:
                project_name (str): Optional: Technical project name.
            """
            command = BuildCommand(
                project_name=project_name
            )
            command.build()
