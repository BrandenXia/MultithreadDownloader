import threading
import requests


class DownloadThread(threading.Thread):
    def __init__(self, name):
        super().__init__(name=name)
