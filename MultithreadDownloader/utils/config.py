import json
import os
from pathlib import Path
from typing import Any
from typing import Literal

from MultithreadDownloader.utils import system_directorys
from MultithreadDownloader.utils.logger import logger

CONFIG_TYPES = Literal["download"]
CONFIG_KEYS = Literal["max_threads", "max_downloads", "download_path", "split_num"]

DEFAULT_CONFIG: dict[str, dict[str, Any]] = {
    "download": {
        "max_threads": os.cpu_count(),
        "max_downloads": 3,
        "download_path": str(system_directorys.get_download_directory()),
        "split_num": 8
    }
}

CONFIG_PATH: Path = system_directorys.get_config_directory() / "config.json"

# Check if config file exists
if not Path.exists(CONFIG_PATH):
    # If not, create it
    logger.info("Config file not found, creating...")
    with open(CONFIG_PATH, "wb") as f:
        f.write(json.dumps(DEFAULT_CONFIG, indent=4).encode("utf-8"))

# Load config file
with open(CONFIG_PATH, "rb") as f:
    CONFIG: dict[str, Any] = json.loads(f.read().decode("utf-8"))
logger.info("Config loaded.")


def get_config(config_type: CONFIG_TYPES, key: CONFIG_KEYS) -> Any:
    """
    Get config by key.
    :param config_type: type of config
    :param key: key of config
    :return: value of config
    """
    return CONFIG[config_type][key]


def save_config(config_type: CONFIG_TYPES, key: CONFIG_KEYS, value: Any) -> None:
    """
    Save config by key.
    :param config_type: type of config
    :param key: key of config
    :param value: value of config
    :return: None
    """
    CONFIG[config_type][key] = value
    with open(CONFIG_PATH, "wb") as config_file:
        config_file.write(json.dumps(CONFIG, indent=4).encode("utf-8"))
    logger.info("Config saved.")
