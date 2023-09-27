"""
oGen - odoo Command Line Interface - Helper tool for developers working on multiple odoo projects
"""

import click

from .commands import CreateCommand
from .commands import BuildCommand
from .commands import ControlCommand
from .commands import InfoCommand

from .constants import VERSION


@click.group(no_args_is_help=True, invoke_without_command=True)
@click.option('-v', '--version', flag_value=True, help='Show installed version of ogen')
def gen(version=False):
    """
    Generator definition as group of commands.
    Running oGen without a command will trigger the help info.
    """
    if version:
        click.echo(f'oGen version {VERSION}')


CreateCommand.init(gen)
BuildCommand.init(gen)
ControlCommand.init(gen)
InfoCommand.init(gen)
