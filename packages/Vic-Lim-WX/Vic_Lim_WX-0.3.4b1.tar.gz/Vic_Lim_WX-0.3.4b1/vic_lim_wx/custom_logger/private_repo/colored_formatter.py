import logging

from colorama import Fore

from ..public.logger_config import LoggerConfig


class ColoredFormatter(logging.Formatter):
    """
    Responsibility:
        - Set the respective colour code to the respective log level, defined
          by config_logger.ini file.

    Attributes:
        logger_config (vic_lim_wx.LoggerConfig): A loggerConfig instance with
        the required attributes defined by config_logger.ini
    """

    def __init__(self, logger_config: LoggerConfig):
        """
        Responsibility:
            - Create a coloredFormatter instance.
            - Stores the configured configparser configured from Logger Config
              Factory

        Args:
            logger_config (vic_lim_wx.LoggerConfig): A loggerConfig instance
            with the required attributes defined by config_logger.ini
        """
        self.logger_config = logger_config
        super().__init__(self.logger_config.get_format())

    def format(self, record: logging.LogRecord):
        """
        Responsibility:
            - Create a coloredFormatter instance.
            - Stores the configured configparser configured from Logger Config
              Factory
        Args:
            record: (logging.LogRecord)
        Returns:
            message: (str)
        """
        COLOR_MAPPING = {
            'black': Fore.BLACK,
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE,
            'reset': Fore.RESET
        }
        COLORS_FOR_STATUS = {
            'DEBUG': COLOR_MAPPING[
                self.logger_config.get_color(log_level="debug")],
            'INFO': COLOR_MAPPING[
                self.logger_config.get_color(log_level="info")],
            'WARNING': COLOR_MAPPING[
                self.logger_config.get_color(log_level="warning")],
            'ERROR': COLOR_MAPPING[
                self.logger_config.get_color(log_level="error")],
            'CRITICAL': COLOR_MAPPING[
                self.logger_config.get_color(log_level="critical")],
            'RESET': COLOR_MAPPING[
                self.logger_config.get_color(log_level="reset")
            ]
        }

        log_message = super().format(record)
        RESET = COLORS_FOR_STATUS.get("RESET")
        log_level_color = COLORS_FOR_STATUS.get(record.levelname)
        return f"{log_level_color}{log_message}{RESET}"
