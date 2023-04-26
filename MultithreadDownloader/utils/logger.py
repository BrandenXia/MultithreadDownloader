from loguru import logger

from MultithreadDownloader.utils import system_directorys

# create log directory
INFO_LOG = system_directorys.get_config_directory() / "info.log"
ERROR_LOG = system_directorys.get_config_directory() / "error.log"

# logger configuration
logger.add(str(INFO_LOG), format="{time} {level} {message}", level="INFO", rotation="1 MB", compression="zip")
logger.add(str(ERROR_LOG), format="{time} {level} {message}", level="ERROR", rotation="1 MB", compression="zip")
