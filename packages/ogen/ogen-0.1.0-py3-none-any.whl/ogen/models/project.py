"""Project definition and dedicated functionality"""

import os
import dataclasses
import configparser
import yaml
import click

from .abstract.base_config import BaseConfig

from ..constants import DEF_STRUCTURE_YML
from ..constants import DEF_PROJECT_STRUCTURE
from ..constants import DEF_ODOO_VERSION
from ..constants import DEF_ODOO_REPO
from ..constants import ODOO_SHALLOW_CLONE
from ..constants import EXPECTED_KEY_PATHS
from ..exceptions import \
    ConfigError, \
    IntegrityError, \
    UserAbortError, \
    InputError

from ..utils.helper import validate_yml_file
from ..utils.helper import validate_project_name
from ..utils.helper import validate_odoo_version
from ..utils.helper import generate_password
from ..utils.helper import execute_command
from ..utils.git import GitUtils
from ..utils.docker_file import DockerFile
from ..utils.docker_compose import DockerCompose as DC


def use_project_path(func: callable) -> callable:
    """
    Decorator that switches the current working directory
    to project's path before executing the wrapped function
    and switches back to original path after its execution.

    Args:
        func (function): Function being decorated
    """
    def inner(*args, **kwargs):
        # Get current directory
        orig_path = os.getcwd()

        project = args and args[0] or False

        if not project or not isinstance(project, Project):
            raise IntegrityError(
                'The @use_project_path decorator can be applied '
                'only to a member function of the Project class.')

        # Switch current directory to project's path
        os.chdir(project.data.project_path)

        res = func(*args, **kwargs)

        # Switch current directory to original path
        os.chdir(orig_path)
        return res

    return inner


@dataclasses.dataclass
class ProjectData:  # pylint: disable=too-many-instance-attributes
    """
    Data Class that keeps the project main attributes
    """
    project_name: str = ''
    odoo_version: str = DEF_ODOO_VERSION
    addons_repo: str = ''
    no_build: bool = False
    project_structure: str = DEF_STRUCTURE_YML

    create_mode: bool = False
    workspace_path: str = ''
    project_path: str = ''
    docker_network_name: str = ''
    pg_pass: str = ''


class Project(BaseConfig):
    """
    Definition of a project
    """

# region Class properties

    data: ProjectData
    command: 'BaseCommand'

    key_paths: dict
    git_repos: dict

# endregion

# region Class Init

    def __init__(self, command: 'BaseCommand', project_data: dict) -> None:

        self._prepare_project_data(project_data)
        validate_project_name(self.name)

        self.command = command
        self.data.create_mode = self.command.mode == 'create'

        # Prepare config path
        self._set_config_attrs()
        # and init config
        super().__init__()

        validate_odoo_version(self.data.odoo_version)
        validate_yml_file(self.data.project_structure)

    @property
    def name(self) -> str:
        """
        Shortly return project's name.

        Returns:
            str: Project's name
        """
        return self.data.project_name

    def _prepare_project_data(self, input_data: dict) -> None:
        """
        Parses the input data and initializes the ProjectData object.

        Args:
            input_data (dict): the project_data received by __init__
        """
        project_data = ProjectData()

        for data_field in dataclasses.fields(ProjectData):
            val = input_data.get(data_field.name, None)
            if not val:
                continue
            setattr(project_data, data_field.name, val)
        self.data = project_data

# endregion

# region Config

    def _set_config_attrs(self):
        workspace_dir = self.command.get_config('workspace_dir')

        if not workspace_dir:
            raise ConfigError(
                f'Cannot determine workspace_dir for the project {self.name}')

        self.data.workspace_path = workspace_dir
        self.data.project_path = os.path.join(
            workspace_dir, self.name)

        # Check if project already exists when create is executed
        if self.data.create_mode and os.path.isdir(self.data.project_path):
            raise IntegrityError(
                f'A directory "{self.name}" '
                f'already exists in "{self.data.workspace_path}"'
            )

        self._config_path = self.data.project_path
        self._config_file = '.ogen.conf'

    def get_default_config(self) -> dict:
        return {
            'DEFAULT': {
                'project_name': self.name,
                'odoo_version': self.data.odoo_version,
            }
        }

# endregion

# region STEP 1: Create project structure

    def create_structure(self):
        """
        Generates the folders structure of the project
        """
        project_structure = self.get_structure()

        green_project_name = click.style(self.name, fg='green')
        click.echo(f'Creating project "{green_project_name}" using '
                   f'"{self.data.project_structure}" structure '
                   f'and Odoo version {self.data.odoo_version}')

        self.key_paths = {
            'project': self.data.project_path
        }
        self.git_repos = {}

        self._create_structure(project_structure, self.data.project_path)

        self.save_config()

    def _create_structure(self, struct: dict, path: str) -> None:
        """
        Recursive function that generates a folders structure based on input definition.

        Args:
            struct (dict): Structure definition
            path (str): Destination path
        """
        for key, val in struct.items():
            f_path = os.path.join(path, key)

            # Update the path in the key_paths dict
            f_key = val.get('key', False)
            if f_key:
                self.key_paths.update({f_key: f_path})

            # Update the path in the key_paths dict
            repo = val.get('repo', False)
            if repo:
                self.git_repos.update({f_key: repo})

            if val['type'] == 'file':
                with open(f_path, 'w', encoding='utf8'):
                    pass

                continue

            os.makedirs(f_path)

            if 'childs' in val:
                self._create_structure(val.get('childs'), f_path)

    def get_structure(self) -> dict:
        """
        Reads the project structure configured in the structure yml file.

        Returns:
            dict: the project structure
        """
        # struct_file_name = DEF_STRUCTURE_YML

        # if custom_structure and validate_yml_file(custom_structure):
        #     struct_file_name = custom_structure

        struct_file_path = os.path.join(
            self.command.conf_dir, self.data.project_structure)

        if not os.path.exists(struct_file_path):
            if self.data.project_structure != DEF_STRUCTURE_YML:
                raise ConfigError(
                    f'The file {self.data.project_structure} '
                    'supposed to define the project structure, doesn\'t exist'
                )
            self.create_default_structure()

        with open(struct_file_path, 'r', encoding='utf8') as yml_file:
            data = yaml.load(yml_file, Loader=yaml.SafeLoader)

        self._validate_structure(data)

        return data

    def create_default_structure(self):
        """
        Generates the default.yml file that represents default structure supported by oGen
        """
        f_path = os.path.join(self.command.conf_dir, DEF_STRUCTURE_YML)

        click.echo(f'Default structure definition not found.{os.linesep}'
                   f'Generating default structure in {f_path}')

        # Save the yml file
        with open(f_path, 'w', encoding='utf8') as yml_file:
            yml_file.writelines([
                f'# This is the default project structure for oGen{os.linesep}',
                f'# !!! Do not change this file{os.linesep}',
                '# If you need a custom structure copy this file and then run the '
                f'`ogen create [PROJECT_NAME] -s [CUSTOM_NAME].yml`{os.linesep}',
                os.linesep
            ])

            yaml.dump(DEF_PROJECT_STRUCTURE, yml_file)

    def _validate_structure(self, struct: dict, is_root: bool = True, key_items=None):
        """
        Validates the project structure as follows:
        - Makes sure that every item in the structure is a dir or file
        - Makes sure that all necessary files are specified
        """

        key_items = key_items if isinstance(key_items, list) else []
        invalid_conf_msg = \
            f'Invalid project structure in {self.data.project_structure}.{os.linesep}'
        if not isinstance(struct, dict):
            raise ConfigError(f'{invalid_conf_msg}- Invalid file format.')

        for key, val in struct.items():
            if not isinstance(val, dict):
                raise ConfigError(
                    f'{invalid_conf_msg}- Invalid value at key "{key}"')

            f_type = val.get('type', False)
            if not f_type:
                raise ConfigError(
                    f'{invalid_conf_msg}- Invalid type for "{key}"')

            f_key = val.get('key', False)
            if f_key:
                key_items.append(f_key)

            if 'childs' in val:
                self._validate_structure(
                    val['childs'], is_root=False, key_items=key_items)

        if not is_root:
            return

        # Make sure all following keys are in the configured structure
        expected_keys = set(EXPECTED_KEY_PATHS)

        if len(set(key_items).intersection(expected_keys)) != len(expected_keys):
            raise ConfigError(
                f'{invalid_conf_msg}- Expected key items are not found')

# endregion

# region STEP 2: Process Key Paths

    def process_key_paths(self) -> None:
        """
        Part of the project structure there might be some paths that require further processing,
        like
        - Cloning a repo
        - Populating a file
        - etc
        """
        for key in EXPECTED_KEY_PATHS:
            key_action = f'_key_path_{key}'

            if key not in self.key_paths or not hasattr(self, key_action):
                continue

            path = self.key_paths[key]

            f_key_action = getattr(self, key_action)
            if not callable(f_key_action):
                continue

            f_key_action(path)

    def _key_path_odoo(self, path: str) -> None:
        """
        Triggers the action clone odoo sources inside the odoo folder

        Args:
            path (str): The path to the odoo folder
        """
        odoo_repo = self.git_repos.get('odoo', DEF_ODOO_REPO)

        git = GitUtils(repo=odoo_repo,
                       branch=self.data.odoo_version,
                       shallow=ODOO_SHALLOW_CLONE)
        git.clone(path)

    def _key_path_custom_addons(self, path: str) -> None:
        """
        Triggers the action clone repo or only create an empty requirements.txt file

        Args:
            path (str): The path to the addons folder
        """
        addons_repo = self.data.addons_repo \
            or self.git_repos.get('custom_addons', None)

        if not addons_repo:
            # Create an empty requirements.txt file.
            with open(os.path.join(path, 'requirements.txt'), 'w', encoding='utf8'):
                pass

            return

        git = GitUtils(repo=addons_repo)
        git.clone(path)

    def _key_path_docker_file(self, path: str) -> None:
        """
        Triggers the action to add content to the dockerfile

        Args:
            path (str): The path to the dockerfile
        """
        docker_file = DockerFile(self.data.odoo_version, self.key_paths)

        with open(path, 'w', encoding='utf8') as file_handle:
            file_handle.write(docker_file.get_content())

        docker_path = os.path.dirname(path)

        with open(os.path.join(docker_path, 'entrypoint.sh'), 'w', encoding='utf8') \
                as file_handle:
            file_handle.write(docker_file.get_entrypoint_content())

        with open(os.path.join(docker_path, 'wait-for-psql.py'), 'w', encoding='utf8') \
                as file_handle:
            file_handle.write(docker_file.get_wait_sql_content())

    def _key_path_docker_compose(self, path: str) -> None:
        """
        Triggers the action to add content to the docker_compose.yml file.

        Args:
            path (str): The path to the docker_compose.yml file
        """
        docker_compose = DC(self.key_paths, self.name)

        with open(path, 'w', encoding='utf8') as file_handle:
            file_handle.write(docker_compose.get_content())

        self.data.docker_network_name = docker_compose.network_name

    def _ensure_pg_pass(self):
        if self.data.pg_pass:
            return
        self.data.pg_pass = generate_password()

    def _key_path_odoo_conf(self, path: str) -> None:
        """
        Triggers the action to populate the odoo.conf file.

        Args:
            path (str): The path to odoo.conf file
        """
        config = configparser.ConfigParser()
        admin_pass = generate_password()

        self._ensure_pg_pass()

        config['options'] = {
            'admin_passwd': admin_pass,
            'addons_path': ','.join([
                '/mnt/odoo/odoo/addons',
                '/mnt/odoo/addons',
                '/mnt/addons'
            ]),
            'data_dir': '/var/lib/odoo',
            'db_host': 'db',
            'db_port': '5432',
            'db_user': 'odoo',
            'db_password': self.data.pg_pass,
            'db_name': self.name,
        }

        with open(path, 'w', encoding='utf8') as file_handle:
            config.write(file_handle)

    def _key_path_env_file(self, path: str) -> None:
        """
        Triggers the action to populate the .env file.

        Args:
            path (str): The path to .env file
        """
        self._ensure_pg_pass()

        env = {
            'POSTGRES_USER': 'odoo',
            'POSTGRES_PASSWORD': self.data.pg_pass
        }

        env_content = os.linesep.join([f'{k}="{v}"' for k, v in env.items()])

        with open(path, 'w', encoding='utf8') as file_handle:
            file_handle.write(env_content)

# endregion

# region STEP 3: Build docker image

    @use_project_path
    def build(self) -> None:
        """
        Builds the docker image
        """
        if self.data.no_build:
            click.echo('Skip building the docker image')
            click.echo('Execute this later by running `ogen build`')
            return
        DC.build(no_cache=True)

        if not self.data.docker_network_name:
            self.data.docker_network_name = f'net_{self.name}'

        DC.create_network(self.data.docker_network_name)

# endregion

# region Service Control

    def _get_active_project(self) -> 'Project':
        """
        Retrieves the name of the currently active project.
        """
        project_name = self.command.get_config('active_project')
        if project_name == self.name:
            return self

        return Project(
            command=self.command,
            project_data={
                'project_name': project_name
            })

    def _activate(self):
        """
        Sets current project as being active in oGen's config file.
        """
        self.command.set_config('active_project', self.name)

    @use_project_path
    def start(self) -> None:
        """
        Starts the current project

        Raises:
            IntegrityError: In case the project is already running.
            UserAbortError: In case another project is running and the user doesn't want to sop it.
        """
        active_project = self._get_active_project()

        if active_project.is_running():
            if active_project == self:
                raise IntegrityError(
                    f'The containers for project `{self.name}` are already running',
                    show_details=False)

            click.echo(
                f'The project `{active_project.name}` is currently '
                'running and needs to be stopped.')

            # Get user's confirmation to stop the running project
            cont = click.confirm(f'Stop `{active_project.name}`?',
                                 default=True)
            if not cont:
                raise UserAbortError(
                    f'In order to run `{self.name}`, '
                    f'you first need to stop `{active_project.name}`.')
            active_project.stop()

        self._activate()

        click.echo(
            f'Starting the docker containers for project `{self.name}`...')

        # Check if odoo service exists
        current_status = DC.status()
        if not current_status.get('odoo', False):
            DC.up()
            return

        DC.start()

    @use_project_path
    def is_running(self) -> bool:
        """
        Checks if `odoo` and `db` for current project are running.
        """
        status = DC.status(running=True)

        return bool(status.get('odoo', False))

    @use_project_path
    def restart(self) -> None:
        """
        Restarts the current project
        """
        click.echo(
            f'Restarting the docker containers for project `{self.name}`...')

        DC.stop()
        DC.start()

    @use_project_path
    def stop(self, down: bool = False) -> None:
        """
        Stops the current project

        Args:
            down (bool, optional): Use down instead of stop to remove the containers.
                                   Defaults to False.
        """
        click.echo(
            f'Stopping the docker containers for project `{self.name}`...')

        if down:
            DC.down()
            return

        DC.stop()

# endregion

# region Info

    @use_project_path
    def show_logs(self, follow: bool = False, service: str = '') -> None:
        """
        Show or follow the logs of all or specified container.

        Args:
            service (str, optional): Service to display the logs for. Defaults to ''.
            follow (bool, optional): Follow log output. Defaults to False.
        """
        click.echo(
            f'Showing logs for the project `{self.name}`...')

        command = ['docker', 'compose', 'logs']
        if follow:
            command.append('--follow')

        if service:
            # Getting services from the docker compose
            service_lines = execute_command(
                ['docker', 'compose', 'ps', '--services'], return_output=True)
            services = service_lines.split(os.linesep)
            if service not in services:
                raise InputError(
                    f'Invalid value "{service}" for a service. Allowed values: {services}')

            command.append(service)

        execute_command(command)

    @use_project_path
    def show_status(self):
        """
        Outputs status info about the project
        """
        click.echo(f'  Name: {self.name}')
        click.echo(f'  Path: {self.data.project_path}')
        click.echo('  Containers:')

        status = DC.status()
        for service, cont_data in status.items():
            state = cont_data['state']
            if state == 'exited':
                state += f", code {cont_data['exit_code']}"
            click.echo(f'    - {service}: {state}')

# endregion
