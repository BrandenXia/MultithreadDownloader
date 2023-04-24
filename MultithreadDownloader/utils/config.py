import json
import os

from pathlib import Path
from typing import Any, Dict

from MultithreadDownloader.utils import system_directorys
from MultithreadDownloader.utils.logger import logger

DEFAULT_CONFIG: dict = {
    "download": {
        "max_threads": os.cpu_count(),
        "max_downloads": 3,
        "download_path": str(system_directorys.get_download_directory())
    }
}

CONFIG_PATH: Path = Path("./config/config.json")

# Check if config file exists
if not Path.exists(CONFIG_PATH):
    # If not, create it
    logger.info("Config file not found, creating...")
    with open(CONFIG_PATH, "wb") as f:
        f.write(json.dumps(DEFAULT_CONFIG, indent=4).encode("utf-8"))

# Load config file
with open(CONFIG_PATH, "rb") as f:
    CONFIG: Dict[str, Any] = json.loads(f.read().decode("utf-8"))
logger.info("Config loaded.")


def get_config(key: str) -> Any:
    """Get config by key."""
    return CONFIG[key]


def save_config(key: str, value: Any) -> None:
    """Save config by key."""
    CONFIG[key] = value
    with open(CONFIG_PATH, "wb") as config_file:
        config_file.write(json.dumps(CONFIG, indent=4).encode("utf-8"))
    logger.info("Config saved.")
