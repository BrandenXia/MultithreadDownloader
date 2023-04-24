import os
import pathlib

from queue import Queue


class DownloadManager:
    def __init__(self, max_threads: int = os.cpu_count(), max_downloads: int = 3, download_path: str = None):
        self.download_queue = Queue()
        self.downloading = Queue()
        self.downloaded = []
