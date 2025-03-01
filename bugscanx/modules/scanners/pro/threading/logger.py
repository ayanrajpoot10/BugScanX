import os
import sys
import logging
from threading import RLock

class Logger:
    def __init__(self, level='DEBUG'):
        self._lock = RLock()
        self.logger = logging.getLogger('bugscanx')
        self.logger.setLevel(getattr(logging, level))
        
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter('\r\033[2K{message}\033[0m', style='{'))
        self.logger.addHandler(handler)

    def replace(self, message):
        cols = os.get_terminal_size()[0]
        msg = message[:cols - 3] + '...' if len(message) > cols else message
        with self._lock:
            sys.stdout.write(f'\033[2K{msg}\033[0m\r')
            sys.stdout.flush()

    def log(self, message, level='INFO'):
        getattr(self.logger, level.lower())(message)
