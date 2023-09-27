"""Dedicated space for `create` project command."""

from typing import Union
import click

from ..models.abstract.base_command import BaseCommand
from ..models.project import Project
from ..exceptions import handle_error


class CreateCommand(BaseCommand):
    """
    Class that handles specific part of creating a new Odoo development project.
    """

    mode: str = 'create'

    @handle_error
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self.project = Project(
            command=self,
            project_data=kwargs)

    @handle_error
    def execute(self) -> None:
        """
        Main function called to execute the `create` command
        """
        self.project.create_structure()

        self.project.process_key_paths()

        self.project.build()

        active_project = self.get_config('active_project')
        if not active_project:
            self.set_config('active_project', self.project.name)

        self.save_config()

    @staticmethod
    def init(gen) -> None:
        """
        Attaches the `create` command to the Generator.

        Argument:
            gen: The `gen` group function.
        """

        @gen.command(help='Create a new project')
        @click.argument('project_name', required=True)
        @click.option('-s', '--structure',
                      help='Custom project structure defined in configuration folder.')
        @click.option('-v', '--odoo-version',
                      help='Version of Odoo to be checked out.')
        @click.option('-r', '--addons-repo',
                      help='Git repository to be cloned into custom_addons folder.')
        @click.option('-n', '--no-build',
                      flag_value=True,
                      help='Don\'t build the docker image. '
                           'This implies that the action will be triggered manually later.')
        def create(project_name: str,
                   structure: Union[str, None] = None,
                   odoo_version: Union[str, None] = None,
                   addons_repo: Union[str, None] = None,
                   no_build: bool = False) -> None:
            """
            Entrypoint for the project `create` command.

            Args:
                project_name (str): Technical project name.
            """
            command = CreateCommand(
                project_name=project_name,
                odoo_version=odoo_version,
                addons_repo=addons_repo,
                no_build=no_build,
                project_structure=structure
            )
            command.execute()
