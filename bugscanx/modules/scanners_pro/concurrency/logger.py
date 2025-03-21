import os
import sys
import logging
from threading import RLock

class Logger:
    COLORS = {
        'ORANGE': '\033[33m',
        'MAGENTA': '\033[35m',
        'CYAN': '\033[36m',
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

    def __init__(self, level='DEBUG'):
        self._lock = RLock()
        self.logger = logging.getLogger('bugscanx')
        self.logger.setLevel(getattr(logging, level))
        
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter('\r\033[2K{message}\033[0m', style='{'))
        self.logger.addHandler(handler)

    def replace(self, message):
        cols = os.get_terminal_size()[0]
        msg = f"{message[:cols - 3]}..." if len(message) > cols else message
        with self._lock:
            sys.stdout.write(f'{self.CLEAR_LINE}{msg}{self.RESET}\r')
            sys.stdout.flush()

    def log(self, message, level='INFO'):
        getattr(self.logger, level.lower())(message)
