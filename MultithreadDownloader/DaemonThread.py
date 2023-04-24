import threading


class DaemonThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)