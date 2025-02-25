__version__ = "1.1.6"

import threading

# Preload Common Modules in background to reduse time while using them
def import_modules_in_background():
    def import_task():
        try:
            from bugscanx.modules.scanners import sub_scan
            from bugscanx.modules.scanners.pro import main_pro_scanner
            from bugscanx.modules.scrappers.subfinder import sub_finder
        except ImportError:
            pass

    thread = threading.Thread(target=import_task, daemon=True)
    thread.start()

import_modules_in_background()