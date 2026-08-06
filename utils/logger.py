from loguru import logger
from config.settings import Settings

import sys

logger.remove()  # Remove the default logger configuration

logger.add(
    sys.stdout,
    level = Settings.log_console_level,
    format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
)

logger.add(
    Settings.log_file,
    level = Settings.log_file_level,
    rotation = '10 MB',
    retention = '7 days',
    compression = 'zip',
)