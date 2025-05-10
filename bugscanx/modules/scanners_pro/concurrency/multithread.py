import time
from queue import Queue
from threading import Thread, RLock

from .logger import Logger

class MultiThread:
    def __init__(self, logger=None, task_list=None, threads=None):
        self._lock = RLock()
        self._loop = True
        self._queue_task_list = Queue()
        self.logger = logger or Logger()

        self._task_list = task_list or []
        self._task_list_total = 0
        self._task_list_scanned_total = 0
        self._task_list_success = []

        self._threads = threads or 50

    def set_threads(self, threads):
        self._threads = threads or self._threads

    def add_task(self, data):
        self._queue_task_list.put(data)
        self._task_list_total += 1

    def get_task_list(self):
        return self._task_list

    def start(self):
        try:
            for task in self.get_task_list():
                self.add_task(task)
            self.init()
            self.start_threads()
            self.join()
        except KeyboardInterrupt:
            pass

    def start_threads(self):
        for _ in range(min(self._threads, self._queue_task_list.qsize()) or self._threads):
            Thread(target=self.thread, daemon=True).start()

    def thread(self):
        while self.loop():
            task = self._queue_task_list.get()
            if not self.loop():
                break
            self.task(task)
            self._task_list_scanned_total += 1
            self._queue_task_list.task_done()

    def init(self):
        pass

    def task(self, *_):
        pass

    def join(self):
        self._queue_task_list.join()
        self.task_complete()
        self.complete()

    def complete(self):
        pass

    def lock(self):
        return self._lock

    def lock_queue(self):
        return self._queue_task_list.mutex

    def loop(self):
        return self._loop

    def success_list(self):
        return self._task_list_success

    def task_success(self, data):
        self._task_list_success.append(data)

    def task_complete(self):
        self._loop = False

        with self.lock_queue():
            self._queue_task_list.unfinished_tasks -= len(self._queue_task_list.queue)
            self._queue_task_list.queue.clear()

    def log(self, *args, **kwargs):
        self.logger.log(*args, **kwargs)

    def log_replace(self, *messages):
        default_messages = [
            f'{self.percentage_scanned():.3f}%',
            f'{self._task_list_scanned_total} of {self._task_list_total}',
            f'{len(self.success_list())}',
        ]

        messages = [str(x) for x in messages if x is not None and str(x)]
        
        self.logger.replace(' - '.join(default_messages + messages))

    def sleep(self, seconds):
        while seconds > 0:
            yield seconds
            time.sleep(1)
            seconds -= 1

    def percentage(self, data_count):
        return (data_count / max(self._task_list_total, 1)) * 100

    def percentage_scanned(self):
        return self.percentage(self._task_list_scanned_total)
