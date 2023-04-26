import os

from pathlib import Path


def get_download_directory() -> Path:
    """
    Get the download directory from the config file.
    :return: The download directory.
    """
    # Solution from https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder
    if os.name == "nt":  # Windows
        import winreg
        sub_key: str = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid: str = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = Path(winreg.QueryValueEx(key, downloads_guid)[0])
    else:  # Linux / Mac
        location = Path.home() / "Downloads"
    if not location.exists():
        Path.mkdir(location, parents=True, exist_ok=True)
    return location


def get_config_directory() -> Path:
    """
    Get the config directory from the config file.
    :return: The config directory.
    """
    if os.name == "nt":  # Windows
        location = Path.home() / "AppData" / "Roaming" / "MultithreadDownloader"
    else:  # Linux / Mac
        location = Path.home() / ".config" / "MultithreadDownloader"
    if not location.exists():
        Path.mkdir(location, parents=True, exist_ok=True)
    return location


def get_log_directory() -> Path:
    """
    Get the log directory from the config file.
    :return: The log directory.
    """
    if os.name == "nt":  # Windows
        location = Path.home() / "AppData" / "Local" / "MultithreadDownloader"
    else:  # Linux / Mac
        location = Path.home() / ".local" / "share" / "MultithreadDownloader"
    if not location.exists():
        Path.mkdir(location, parents=True, exist_ok=True)
    return location
