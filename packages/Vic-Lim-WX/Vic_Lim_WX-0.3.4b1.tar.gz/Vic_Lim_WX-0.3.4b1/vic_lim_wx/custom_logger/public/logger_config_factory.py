import configparser
import os

from vic_lim_wx.custom_logger.public.logger_config import LoggerConfig
from ..private_repo.error_configuration import ConfigurationError


class LoggerConfigFactory:
    """
    Responsibility:
        - Creates an instance of LoggerConfig.

    Attributes:
        config_file_path (str): the specified configuration file.

    Raises:
        ConfigurationError: If there is an issue with the specified
        configuration file.

    """

    def __init__(self, config_file_path: str) -> None:
        self.config_parser = configparser.ConfigParser()
        self.config_file_path: str = config_file_path
        self._validate_file_path(config_file_path)
        self._read_config_file()

    def _validate_file_path(self, config_file_path: str):
        """
        Responsibility:
            - Performs the following checks to the specified configuration
              file:
                1. Check if configuration file exist
                2. Check if the file provided is a file.
                3. Check if the file is readable

        Args:
            config_file_path (str): The path to the configuration INI file.

        Raises:
            ConfigurationError: If there is an error while reading the INI file.

        """
        if not os.path.exists(config_file_path):
            raise ConfigurationError(
                f"Configuration file not found at path: {config_file_path}")
        if not os.path.isfile(config_file_path):
            raise ConfigurationError(
                f"Invalid configuration file: {config_file_path} is not "
                f"a regular file")
        if not os.access(config_file_path, os.R_OK):
            raise ConfigurationError(
                f"Configuration file is not readable: {config_file_path}")

    def _read_config_file(self):
        """
        Responsibility:
            - Reads configuration settings from the specified configuration
              file.

        Raises:
            ConfigurationError: If there is an error while reading the INI
            file.
        """
        try:
            self.config_parser.read(self.config_file_path)
        except configparser.Error as e:
            raise ConfigurationError(
                f"Error while reading configuration file: {e}")

    def create_logger_config(self) -> LoggerConfig:
        return LoggerConfig(self.config_parser)
