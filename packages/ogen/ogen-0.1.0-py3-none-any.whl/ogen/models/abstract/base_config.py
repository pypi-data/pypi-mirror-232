"""
Abstract definition used in models that have a config
"""
import os
import configparser
import click

from ...exceptions import ConfigError


class BaseConfig:
    """
    Abstract class inherited by models that store a configuration
    """

    _config: dict
    _config_header: str = ''
    _config_path: str
    _config_file: str

    def __init__(self):
        self.load_config()

    @property
    def _config_file_path(self) -> str:
        """
        The path to the configuration file

        Raises:
            NotImplementedError: if _config_path is not set
            NotImplementedError: if the _config_file is not set

        Returns:
            str: The path to the configuration file
        """
        if not self._config_path:
            raise NotImplementedError('_config_path is not set')
        if not self._config_file:
            raise NotImplementedError('_config_file is not set')
        return os.path.join(self._config_path, self._config_file)

    def get_default_config(self) -> dict:
        """
        Gets the default configuration

        Raises:
            NotImplementedError: This function needs to be implemented by the inheritors

        Returns:
            dict: A dictionary containing the defult configuration
        """
        raise NotImplementedError

    def load_config(self) -> None:
        """
        Loads the config values from the config file.
        Creates the config file if it doesn't exist.
        """

        if not os.path.isdir(self._config_path):
            os.makedirs(self._config_path)

        # Create new config file with default values if no config exists yet
        if not os.path.exists(self._config_file_path):
            click.echo('Configuration file not found. Attempting to create it.')
            self._config = self.get_default_config()
            return

        config = configparser.ConfigParser()
        self._config = {}

        try:
            config.read(self._config_file_path)
        except configparser.Error as err:
            raise ConfigError(err.message) from err

        for config_item in config.items():
            section_name = config_item[0]
            self._config[section_name] = {}
            for option, value in config[section_name].items():
                self._config[section_name][option] = value

    def save_config(self) -> None:
        """
        Saves the current configuration to the file
        """
        config = configparser.ConfigParser()
        config.read_dict(self._config)

        with open(self._config_file_path, 'w', encoding='utf8') as conf_file:
            if self._config_header:
                conf_file.write(self._config_header)
            config.write(conf_file)

    def get_config(self, key: str, section: str = 'DEFAULT') -> str:
        """
        Returns the value of a configuration parameter

        Args:
            key (str): Parameter name
            section (str, optional): Configuration section. Defaults to 'DEFAULT'.

        Returns:
            str: the value of a configuration parameter
        """
        return self._config.get(section, {}).get(key, '')

    def set_config(self, key: str, value: str, section: str = 'DEFAULT'):
        """
        Stores the value of a configuration parameter

        Args:
            key (str): Parameter name
            value (str): Configuration value
            section (str, optional): Configuration section. Defaults to 'DEFAULT'.
        """
        config = self._config.get(section)
        if not isinstance(config, dict):
            click.echo('Warning: Unable to set the following config value: '
                       f'{section} > {key} : {value}')
            return
        config.update({key: value})
