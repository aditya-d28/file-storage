import json
import logging
import logging.config
import os

from app.core.config import settings

current_directory = os.path.dirname(__file__)
config_path = os.path.join(current_directory, "logger_config.json")


def setup_logger():
    """Set up the logger with configurable log levels for console and file handlers."""
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    if config is None:
        raise Exception("Failed to load logger config files")

    config["handlers"]["console"]["level"] = settings.CONSOLE_LOG_LEVEL
    config["handlers"]["file"]["level"] = settings.FILE_LOG_LEVEL

    logging.config.dictConfig(config)


def get_logger(name: str | None = None) -> logging.Logger:
    """Retrieve a logger with the default formatting."""
    return logging.getLogger(name if name is not None else "system")
