import os
import sys

from loguru import logger


def configure_logging() -> None:
    level = os.getenv("LOGURU_LEVEL", "INFO")
    logger.remove()
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
        level=level,
        enqueue=False,
        colorize=sys.stderr.isatty(),
    )
