import logging
from logging.config import dictConfig

from pydantic import BaseModel

class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "camera_service"
    LOG_FORMAT: str = f"%(levelname)s | {LOGGER_NAME} | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    loggers = {
        LOGGER_NAME: {
            "handlers": ["default", "file_handler"], 
            "level": LOG_LEVEL
            },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file_handler": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/camera_service.log",
            "mode": "a",
            "encoding": "utf-8",
            "maxBytes": 100000, 
            "backupCount": 4
        }
    }

dictConfig(LogConfig().dict())
logger = logging.getLogger(LogConfig().LOGGER_NAME)