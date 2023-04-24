import sys

from loguru import logger


# logger configuration
logger.add("logs/info.log", format="{time} {level} {message}", level="INFO", rotation="1 MB", compression="zip")
logger.add("logs/error.log", format="{time} {level} {message}", level="ERROR", rotation="1 MB", compression="zip")