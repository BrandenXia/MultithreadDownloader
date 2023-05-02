import threading
from collections.abc import Callable
from typing import Literal

import requests

from MultithreadDownloader.download.DownloadThread import DownloadThread
from MultithreadDownloader.utils import config
from MultithreadDownloader.utils.logger import logger

download_status = Literal['canceled', 'finished', 'failed']


class DaemonThread(threading.Thread):
    def __init__(self, parent: 'DownloadManager') -> None:
        super().__init__()
        self._parent: 'DownloadManager' = parent

    def run(self) -> None:
        while True:
            # if thread queue is not empty, check if a thread is finished
            if not self._parent.thread_empty():
                self._parent.clean_thread()

            # if downloading queue is not full and download queue is not empty, add a download to the downloading queue
            if self._parent.downloading_available() and not self._parent.download_empty():
                url: str = self._parent.get_download()
                try:
                    length: int = requests.head(url).headers.get('Content-Length')
                except Exception as e:
                    logger.error(f'Failed to get the length of {url}: ' + str(e))
                    continue
                self._parent.assign_task(url, length)
                self._parent.add_downloading(url, length)

            # if task queue is not empty and thread queue is not full, assign a task to a thread
            if not self._parent.task_empty() and self._parent.thread_available():
                url, start, end = self._parent.get_task()
                thread: DownloadThread = DownloadThread(url, start, end)
                self._parent.add_thread(thread)
                thread.start()


class DownloadManager:
    def __init__(self) -> None:
        # Queue of urls to download
        self._download_queue: list[str] = []
        # Max number of downloads
        self.max_downloads: int = config.get_config("download", "max_downloads")
        # Queue of urls downloading
        self._downloading: list[tuple[str, int]] = []
        # Queue of urls downloaded
        self.downloaded: list[tuple[str, str]] = []
        # Queue of tasks to be done
        self._tasks: list[tuple[str, int, int]] = []
        # Max number of download
        self.max_threads: int = config.get_config("download", "max_threads")
        # Queue of download
        self._threads: list[DownloadThread] = []
        # Number of splits
        self.split_num: int = config.get_config("download", "split_num")
        # Thread lock
        self.lock: threading.Lock = threading.Lock()
        # Daemon thread
        self.daemon: DaemonThread = DaemonThread(self)
        self.daemon.start()

    def with_lock(self, func: Callable) -> Callable:
        """
        Decorator to get the thread lock
        :param func: function to be decorated
        :return: function with thread lock
        """

        def wrapper(*args, **kwargs):
            with self.lock:
                return func(*args, **kwargs)

        return wrapper

    @with_lock
    def add_download(self, url: str) -> None:
        """
        Add a url to the download queue
        :param url: a url to download
        """
        logger.info(f'Add {url} to the download queue')
        self._download_queue.append(url)

    @with_lock
    def get_download(self) -> str:
        """
        Get url from the download queue
        :return: url from the download queue
        """
        logger.debug(f'Get a url from the download queue')
        return self._download_queue.pop(0)

    def download_empty(self) -> bool:
        """
        Check if the download queue is empty
        :return: True if the download queue is empty, False otherwise
        """
        return len(self._download_queue) == 0

    @with_lock
    def add_downloading(self, url: str, length: int) -> None:
        """
        Add a url to the downloading queue
        :param length:
        :param url: a url to download
        """
        logger.info(f'Add {url} to the downloading queue')
        self._downloading.append((url, length))

    @with_lock
    def remove_downloading(self, url: str, length: int) -> None:
        """
        Remove url from the downloading queue
        :param url: url to remove
        :param length: length of the url
        """
        logger.info(f'Remove {url} from the downloading queue')
        self._downloading.remove((url, length))

    def get_downloading_percentage(self, url: str) -> float:
        """
        Get the downloading percentage
        :param url: a url
        :return: downloading percentage
        """
        logger.debug(f'Get the downloading percentage of {url}')
        return sum([thread.percentage for thread in self._threads if thread.url == url])

    def downloading_available(self) -> bool:
        """
        Check if the downloading queue is full
        :return: True if the downloading queue is not full, False otherwise
        """
        return len(self._downloading) < self.max_downloads

    def add_downloaded(self, url: str, status: download_status) -> None:
        """
        Add url to the downloaded queue
        :param url: downloaded url
        :param status: download status, 'canceled', 'finished' or 'failed'
        """
        logger.info(f'Add {url} to the downloaded queue')
        self.downloaded.append((url, status))

    @with_lock
    def add_task(self, url: str, start: int, end: int) -> None:
        """
        Add a task to the task queue
        :param url: url to download
        :param start: start byte
        :param end: end byte
        """
        logger.debug(f'Add a task to the task queue')
        self._tasks.append((url, start, end))

    @with_lock
    def get_task(self) -> tuple[str, int, int]:
        """
        Get a task from the task queue
        :return: a task
        """
        logger.debug(f'Get a task from the task queue')
        return self._tasks.pop(0)

    def task_empty(self) -> bool:
        """
        Check if the task queue is empty
        :return: True if the task queue is empty, False otherwise
        """
        return len(self._tasks) == 0

    @with_lock
    def add_thread(self, thread: DownloadThread) -> None:
        """
        Add a thread to the thread queue
        :param thread: a thread
        """
        logger.debug(f'Add a thread to the thread queue')
        self._threads.append(thread)

    def thread_available(self) -> bool:
        """
        Check if the thread queue is full
        :return: True if the thread queue is not full, False otherwise
        """
        return len(self._threads) < self.max_threads

    def thread_empty(self) -> bool:
        """
        Check if the thread queue is empty
        :return: True if the thread queue is empty, False otherwise
        """
        return len(self._threads) == 0

    @with_lock
    def clean_thread(self) -> None:
        """
        Remove finished download from the thread queue
        """
        logger.debug(f'Cleaning the thread queue')
        [self._threads.remove(thread) for thread in self._threads if not thread.is_alive()]

    def assign_task(self, url: str, length: int) -> None:
        """
        Assign a task to a thread
        :param length: length of the file
        :param url: url to download
        """
        logger.debug(f'Assign a task to a thread')
        for i in range(self.split_num):
            if i == 0:
                start: int = 0
                end: int = length // self.split_num
                self.add_task(url, start, end)
                continue
            start: int = length * i // self.split_num + 1
            end: int = length * (i + 1) // self.split_num
            self.add_task(url, start, end)

    def check_download_finished(self) -> None:
        """
        Check if the download is finished
        """
        for download in self._downloading:
            if self.get_downloading_percentage(download[0]) < 1:
                continue
            else:
                self.remove_downloading(download[0], download[1])
                self.add_downloaded(download[0], "finished")
