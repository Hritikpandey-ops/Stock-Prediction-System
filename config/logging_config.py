"""
Logging configuration for the application.
"""
import logging
import sys
from pathlib import Path
from loguru import logger

from config.settings import get_settings

settings = get_settings()


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
    )
    
    # Add file handler
    log_file = Path("logs/app.log")
    log_file.parent.mkdir(exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )
    
    # Configure standard library logging to use loguru
    class LoguruHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            logger.log(level, record.getMessage())
    
    # Remove existing handlers and add loguru handler
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(LoguruHandler())
    root_logger.setLevel(settings.log_level)


# Initialize logging
setup_logging()