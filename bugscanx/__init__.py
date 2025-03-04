import threading

def import_modules_in_background():
    def import_task():
        try:
            from bugscanx.modules.scanners import host_scanner
            from bugscanx.modules.scanners.pro import main_pro_scanner
            from bugscanx.modules.scrappers.subfinder import sub_finder
        except:
            pass

    thread = threading.Thread(target=import_task, daemon=True)
    thread.start()

import_modules_in_background()