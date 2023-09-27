"""Dedicated space for logs, status, info commands."""

import click

from ..models.abstract.base_command import BaseCommand
from ..exceptions import handle_error
from ..constants import VERSION


class InfoCommand(BaseCommand):
    """
    Class that handles specific informational commands.
    """

    mode: str = 'info'

    @handle_error
    def __init__(self, project_name: str = ''):
        super().__init__()

        self._determine_project(project_name=project_name)

    @handle_error
    def logs(self, follow: bool = False, service: str = '') -> None:
        """
        Function called to retrieve or follow the logs
        """
        self.project.show_logs(follow=follow, service=service)

    @handle_error
    def status(self) -> None:
        """
        Function called to execute the `restart` command
        """
        click.echo(f'oGen version {VERSION}')
        click.echo('--------------------')
        click.echo('Active project:')
        self.project.show_status()

    @staticmethod
    def init(gen) -> None:
        """
        Attaches the `logs`, `info`, `status` commands to the Generator.

        Argument:
            gen: The `gen` group function.
        """

        @gen.command(help='View output from containers')
        @click.argument('service',
                        required=False)
        @click.option('-f', '--follow',
                      flag_value=True,
                      help='Follow log output.')
        def logs(service: str = '', follow: bool = False) -> None:
            """
            Entrypoint for logs command.

            Args:
                service (str, optional): Service to display the logs for. Defaults to ''.
                follow (bool, optional): Follow log output. Defaults to False.
            """
            command = InfoCommand()
            command.logs(follow=follow, service=service)

        @gen.command(help='Shows status info about the active project')
        def status() -> None:
            """
            Entrypoint for the status command.
            """
            command = InfoCommand()
            command.status()
