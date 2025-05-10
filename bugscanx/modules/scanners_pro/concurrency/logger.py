import os
import sys
from threading import RLock

class Logger:
    COLORS = {
        'ORANGE': '\033[33m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
        'LGRAY': '\033[37m',
        'GRAY': '\033[90m',
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
    }
    RESET = '\033[0m'
    CLEAR_LINE = '\033[2K'

    @staticmethod
    def colorize(text, color):
        return f"{Logger.COLORS.get(color, '')}{text}{Logger.RESET}"

    def __init__(self):
        self._lock = RLock()

    def replace(self, message):
        cols = os.get_terminal_size()[0]
        msg = f"{message[:cols - 3]}..." if len(message) > cols else message
        with self._lock:
            sys.stdout.write(f'{self.CLEAR_LINE}{msg}{self.RESET}\r')
            sys.stdout.flush()

    def log(self, message):
        with self._lock:
            sys.stderr.write(f'\r{self.CLEAR_LINE}{message}{self.RESET}\n')
            sys.stderr.flush()
