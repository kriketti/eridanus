import logging
import os
import sys
from logging.config import dictConfig


def configure_logging():
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    if level_name not in logging._nameToLevel:
        level_name = "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                }
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "standard",
                }
            },
            "loggers": {
                "eridanus": {"level": "INFO", "propagate": True},
                "main": {"level": "INFO", "propagate": True},
                "__main__": {"level": "INFO", "propagate": True},
                "werkzeug": {"level": "INFO", "propagate": True},
            },
            "root": {"level": level_name, "handlers": ["stdout"]},
        }
    )
