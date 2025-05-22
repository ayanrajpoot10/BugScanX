import time
from abc import ABC, abstractmethod
from threading import Thread, RLock
from queue import Queue, Empty

from .logger import Logger, CursorManager


class MultiThread(ABC):
    def __init__(self, threads=50):
        self._lock = RLock()
        self._queue = Queue()

        self._total = 0
        self._scanned = 0
        self._success = []

        self.threads = threads

        self.logger = Logger()

    def _add_task(self, task):
        self._queue.put(task)
        self._total += 1

    def start(self):
        print()
        with CursorManager():
            try:
                for task in self.generate_tasks():
                    self._add_task(task)

                self.init()
                workers = [
                    Thread(target=self._worker, daemon=True)
                    for _ in range(min(self.threads, self._queue.qsize() or self.threads))
                ]
                for t in workers:
                    t.start()
                self._queue.join()
                self.complete()
            except KeyboardInterrupt:
                pass
        print()

    def _worker(self):
        while True:
            try:
                task = self._queue.get(timeout=1)
            except Empty:
                return

            try:
                self.task(task)
            except Exception as e:
                self.logger.log(f"Error in task: {e}")
            finally:
                with self._lock:
                    self._scanned += 1
                self._queue.task_done()

    def success(self, item):
        self._success.append(item)

    def get_success(self):
        return self._success

    def log_progress(self, *extra):
        parts = [
            f"{self._scanned / max(1, self._total) * 100:.2f}%",
            f"{self._scanned} / {self._total}",
            f"{len(self._success)}"
        ] + [str(x) for x in extra if x]
        self.logger.replace(" - ".join(parts))

    def sleep(self, seconds):
        while seconds > 0:
            yield seconds
            time.sleep(1)
            seconds -= 1

    @abstractmethod
    def generate_tasks(self): pass

    @abstractmethod
    def init(self): pass

    @abstractmethod
    def task(self, task): pass

    @abstractmethod
    def complete(self): pass
