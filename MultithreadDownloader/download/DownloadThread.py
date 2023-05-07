import threading
import requests

from urllib.parse import urlparse
from os.path import basename

from MultithreadDownloader.utils.system_directorys import get_download_directory


class DownloadThread(threading.Thread):
    def __init__(self, url: str, start_byte: int, end_byte: int) -> None:
        super().__init__(name=url)
        self.url: str = url
        self.start_byte: int = start_byte
        self.end_byte: int = end_byte
        self.percentage: int = 0
        self.path: str = get_download_directory() / basename(urlparse(url).path)

    def run(self) -> None:
        res = requests.get(self.url, headers={'Range': f'bytes={self.start_byte}-{self.end_byte}'}, stream=True)
        with open(self.path, 'rb') as f:
            f.seek(self.start_byte)
            for chunk in res.iter_content(chunk_size=1024):
                f.write(chunk)
                self.percentage += len(chunk)
