"""
Custom Exceptions
"""

import sys
import click


class OCLIError(BaseException):
    "Abstract oGen Exception"

    message: str = 'Unexpected Error'
    details: str = 'Command terminated due to an unexpected error.'
    show_details: bool = True
    abort: bool = True

    def __init__(self, message: str,
                 show_details: bool = True) -> None:
        self.message = message
        self.show_details = show_details
        super().__init__()

    def display_details(self) -> None:
        """
        Outputs the error details to the terminal
        """

        click.echo(self.message)
        if self.show_details:
            click.echo(self.details)


class UserAbortError(OCLIError):
    """
    Exception raised when the user decides to abort.
    """
    details = 'Command terminated by user.'


class ConfigError(OCLIError):
    """
    Exception raised when configuration is invalid.
    """
    details = 'Command terminated due to a configuration error.'


class InputError(OCLIError):
    """
    Exception raised when user provides invalid input.
    """
    details = 'Command terminated due to an invalid input.'


class IntegrityError(OCLIError):
    """
    Exception raised when inconsistency is found and process can't continue.
    """
    details = 'Command terminated due to an inconsistency.'


def handle_error(func: callable) -> callable:
    """
    Decorator that wraps the decorated function
    in a try-except which handles OCLIError

    Args:
        func (function): Function being decorated
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OCLIError as err:
            err.display_details()
            if err.abort:
                sys.exit(1)
        return None

    return inner
