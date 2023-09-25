import logging
import sys

from .logger_config import LoggerConfig
from ..private_repo.colored_formatter import ColoredFormatter


class CustomLogger:
    """
    Responsibility:
        - Stores the configured configparser configured from Logger Config
          Factory

    Attributes:
        logger (logging): A loggerConfig instance with the required
        attributes defined by config_logger.ini
        formatter (ColoredFormatter)

    """

    def __init__(self, logger_config: LoggerConfig,
                 class_name: str = "Not_A_Class"):
        """
        Responsibility:
            - Create a customLogger instance.
            - Stores the configured configparser configured from Logger Config
              Factory
        Args:
            record: (logging.LogRecord)
        Returns:
            message: (str)
        """
        self.logger = logging.getLogger(class_name)
        self.logger.setLevel(logging.DEBUG)

        # Create a formatter
        self.formatter = ColoredFormatter(logger_config)

        # Create a console handler and set the formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
