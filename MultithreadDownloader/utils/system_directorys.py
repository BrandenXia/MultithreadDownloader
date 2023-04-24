import os

from pathlib import Path


def get_download_directory() -> Path:
    """
    Get the download directory from the config file.
    """
    # Solution from https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder
    if os.name == "nt":  # Windows
        import winreg
        sub_key: str = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid: str = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return Path(location)
    else:  # Linux / Mac
        return Path.home() / "Downloads"
