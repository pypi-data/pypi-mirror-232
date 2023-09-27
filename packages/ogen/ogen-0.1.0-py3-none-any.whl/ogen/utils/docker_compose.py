"""
DockerCompose file generator class
"""

import os
import json
import yaml
import click

from ..constants import DEF_DOCKER_COMPOSE_VERSION
from ..constants import DEF_PSQL_VERSION
from .helper import generate_password
from .helper import execute_command


class DockerCompose:  # pylint: disable=too-few-public-methods
    """
    DockerCompose file generator class
    """

# region Init

    compose: dict
    key_paths: dict
    pg_pass: str
    network_name: str

    def __init__(self, key_paths: dict, project_name: str):
        self.key_paths = key_paths
        self.network_name = f'net_{project_name}'

        self.compose = {
            'version': DEF_DOCKER_COMPOSE_VERSION,
            'services': {}
        }

# endregion

# region docker-compose.yml generator

    def _rel_path(self, path_key):
        project_path = self.key_paths.get('project', '')
        return self.key_paths.get(path_key, '').replace(project_path, '.')

    def _add_service(self, serv: dict) -> None:
        self.compose['services'].update(serv)

    def _set_db(self) -> None:

        db_data_path = self._rel_path('db_data')

        self.pg_pass = generate_password()

        db_config = {
            'image': f'postgres:{DEF_PSQL_VERSION}',
            'volumes': [
                f'{db_data_path}:/var/lib/postgresql/data'
            ],
            'env_file': ['.env'],
            'ports': [
                '5432:5432',
            ],
            'networks': [
                self.network_name
            ],
        }
        self._add_service({'db': db_config})

    def _set_odoo(self) -> None:
        dockerfile_path = self._rel_path('docker_file')
        custom_addons_path = self._rel_path('custom_addons')
        conf_dir_path = self._rel_path('conf_dir')
        odoo_path = self._rel_path('odoo')
        odoo_data_path = self._rel_path('odoo_data')

        odoo_config = {
            'build': {
                'context': '.',
                'dockerfile': dockerfile_path
            },
            'volumes': [
                f'{custom_addons_path}:/mnt/addons',
                f'{odoo_path}:/mnt/odoo',
                f'{odoo_data_path}:/var/lib/odoo',
                f'{conf_dir_path}:/etc/odoo/',
            ],
            'env_file': ['.env'],
            'ports': [
                '8069:8069',
                '8071:8071',
                '8072:8072',
            ],
            'depends_on': ['db'],
            'networks': [
                self.network_name
            ]
        }

        self._add_service({'odoo': odoo_config})

    def _set_network(self):
        network_config = {
            self.network_name: {
                'external': True,
                'name': self.network_name
            }
        }

        self.compose.update({'networks': network_config})

    def get_content(self) -> str:
        """
        Aggregates and returns the content of the dockerfile based on specific Odoo version

        Returns:
            str: Content of the dockerfile
        """
        self._set_db()
        self._set_odoo()
        self._set_network()

        return yaml.dump(self.compose)

# endregion

# region Static functions

    @staticmethod
    def build(no_cache: bool = False) -> None:
        """
        Runs the command to build the docker compose

        Args:
            no_cache (bool, optional): Use --no-cache argument. Defaults to False.
        """
        click.echo("Building the docker image...")

        command = ['docker', 'compose', 'build']
        if no_cache:
            command.append('--no-cache')
        execute_command(command)

    @staticmethod
    def create_network(name: str):
        """
        Creates a docker network with the specified name.

        Args:
            name (str): Network's name
        """
        # Check if docker network already exists
        networks = execute_command(
            ['docker', 'network', 'ls', '--format', '{{.Name}}'],
            return_output=True
        ).split(os.linesep)

        for net in networks:
            if net == name:
                click.echo(
                    f'Network `{name}` already exists. Skipping creation.')
                return

        click.echo(f'Creating the `{name}` docker network...')
        execute_command(['docker', 'network', 'create', name],
                        allow_error=True)

    @staticmethod
    def up(detached: bool = True):  # pylint: disable=invalid-name
        """
        Create and start the docker containers.

        Args:
            detached (bool): Detached mode: Run containers in the background
        """
        command = ['docker', 'compose', 'up']
        if detached:
            command.append('--detach')

        execute_command(command)

    @staticmethod
    def down():
        """
        Stop and remove the docker containers.
        """
        command = ['docker', 'compose', 'down']
        execute_command(command)

    @staticmethod
    def start():
        """
        Start the docker containers.
        """
        command = ['docker', 'compose', 'start']
        execute_command(command)

    @staticmethod
    def stop():
        """
        Stop the docker containers.
        """
        command = ['docker', 'compose', 'stop']
        execute_command(command)

    @staticmethod
    def status(running: bool = False) -> dict:
        """
        Retrieves the status of comtainers part of the current compose.
        """
        command = [
            'docker', 'compose', 'ps',
            '--format', 'json'
        ]
        command += ['--status', 'running'] if running else ['--all']

        status_str = execute_command(command=command, return_output=True)

        status = json.loads(status_str)

        res = {}
        if not status:
            return res

        for service in status:
            res[service.get('Service')] = {
                'name': service.get('Name'),
                'id': service.get('ID'),
                'state': service.get('State'),  # running, exited
                'exit_code': service.get('ExitCode')
            }

        return res


# endregion
