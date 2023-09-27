"""Dedicated space for start, restart, stop, etc commands."""

import click

from ..models.abstract.base_command import BaseCommand
from ..exceptions import handle_error


class ControlCommand(BaseCommand):
    """
    Class that handles specific commands of controlling project's activity.
    """

    mode: str = 'control'

    @handle_error
    def __init__(self, project_name: str = ''):
        super().__init__()

        self._determine_project(project_name=project_name)

    @handle_error
    def start(self) -> None:
        """
        Function called to execute the `start` command
        """
        self.project.start()
        self.save_config()

    @handle_error
    def stop(self, down: bool = False) -> None:
        """
        Function called to execute the `stop` command

        Args:
            down (bool, optional): Use down instead of stop to remove the containers.
                                   Defaults to False.
        """
        self.project.stop(down=down)
        self.save_config()

    @handle_error
    def restart(self) -> None:
        """
        Function called to execute the `restart` command
        """
        self.project.restart()
        self.save_config()

    @staticmethod
    def init(gen) -> None:
        """
        Attaches the `start`, `stop`, `restart` commands to the Generator.

        Argument:
            gen: The `gen` group function.
        """

        @gen.command(help='Starts the docker containers for the active project')
        @click.argument('project_name', required=False)
        def start(project_name: str = '') -> None:
            """
            Entrypoint for the project `start` command.

            Args:
                project_name (str): Optional: Technical project name.
            """
            command = ControlCommand(
                project_name=project_name
            )
            command.start()

        @gen.command(help='Stops the docker containers for the active project')
        @click.option('-d', '--down',
                      flag_value=True,
                      help='Use down instead of stop to remove the containers.')
        def stop(down: bool = False) -> None:
            """
            Entrypoint for the project `stop` command.
            """
            command = ControlCommand()
            command.stop(down=down)

        @gen.command(help='Restarts the docker containers for the active project')
        def restart() -> None:
            """
            Entrypoint for the project `restart` command.
            """
            command = ControlCommand()
            command.restart()
