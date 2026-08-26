import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import settings


def ensure_log_directory() -> Path:
    root = Path(__file__).resolve().parent.parent
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def configure_logging() -> None:
    log_dir = ensure_log_directory()
    logger = logging.getLogger()
    logger.setLevel(settings.log_level.upper())

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=5_242_880, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


logger = logging.getLogger("finance_advisor")
