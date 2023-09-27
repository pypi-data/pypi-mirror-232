import logging
import traceback

class Logger:
    """Custom logger wrapping the standard Python logging module."""

    def __init__(self, name: str, level: str) -> None:
        """Initialize the logger with the given name and level."""
        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.propagate = False
        set_level = logging._nameToLevel[level]
        self.logger.setLevel(set_level)
        if not self.logger.handlers:
            msg = '%(levelname)s: %(asctime)s - %(message)s - %(name)s'
            formats: str = msg
            formatter = logging.Formatter(formats)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, message: str) -> None:
        """Log a debug-level message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log an info-level message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning-level message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error-level message and print the traceback."""
        self.logger.error(message)
        print(traceback.format_exc())

    def critical(self, message: str) -> None:
        """Log a critical-level message and print the traceback."""
        self.logger.critical(message)
        print(traceback.format_exc())