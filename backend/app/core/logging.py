import logging
import os
from logging.handlers import RotatingFileHandler

from app.core.config import Settings


def setup_logging(settings: Settings) -> logging.Logger:
    log_dir = os.path.dirname(settings.log_file) or "."
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("pdv")
    logger.setLevel(logging.INFO)

    if not any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers):
        file_handler = RotatingFileHandler(settings.log_file, maxBytes=1_000_000, backupCount=3)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
