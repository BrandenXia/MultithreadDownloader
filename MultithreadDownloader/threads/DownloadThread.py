import threading


class DownloadThread(threading.Thread):
    def __init__(self, url: str, start_byte: int, end_byte: int) -> None:
        super().__init__(name=url)
        self.url: str = url
        self.start_byte: int = start_byte
        self.end_byte: int = end_byte
        self.percentage: float = 0.0
