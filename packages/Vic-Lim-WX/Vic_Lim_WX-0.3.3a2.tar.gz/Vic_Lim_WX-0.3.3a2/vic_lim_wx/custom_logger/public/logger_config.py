import configparser

__all__ = [
    "LoggerConfig"
]


class LoggerConfig:
    """
    Responsibility:
        - Stores the configured configparser configured from Logger Config
          Factory

    Attributes:
        config_parser (configparser.ConfigParser): A configuration parser instance
        as configured by LoggerConfigFactory.

    Raises:
        ConfigurationError: If there is an issue with the specified
        configuration file.
    """

    def __init__(self, config_parser: configparser.ConfigParser):
        """
        Initializes a LoggerConfig instance. Will perform a check on file path
        , and then will proceed to read the specified configuration file if
        there isno error.

        Args:
            config_parser (configparser.ConfigParser): A configuration parser instance
        as configured by LoggerConfigFactory.
        """
        self.config_parser: config_parser = config_parser

    def get_color(self, log_level):
        return self.config_parser.get("Colors", log_level)

    def get_format(self):
        return self.config_parser.get("Format", "log_format")
