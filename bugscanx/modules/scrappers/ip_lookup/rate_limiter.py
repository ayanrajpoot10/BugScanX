import time
from threading import Lock

class RateLimiter:
    def __init__(self, requests_per_second: float):
        self.delay = 1.0 / requests_per_second
        self.last_request = 0
        self._lock = Lock()

    def acquire(self):
        with self._lock:
            now = time.time()
            if now - self.last_request < self.delay:
                time.sleep(self.delay - (now - self.last_request))
            self.last_request = time.time()
