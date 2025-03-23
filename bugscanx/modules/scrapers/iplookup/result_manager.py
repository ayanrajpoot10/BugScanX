from threading import Lock
from .logger import console, IPLookupConsole

class ResultManager:
    def __init__(self, output_file: str, ip_console: IPLookupConsole):
        self.output_file = output_file
        self.total_domains = 0
        self.lock = Lock()
        self.console = ip_console

    def save_result(self, ip, domains):
        if not domains:
            return
            
        with self.lock:
            with open(self.output_file, 'a') as f:
                for domain in domains:
                    f.write(f"{domain}\n")
            self.total_domains += len(domains)
            self.console.update_ip_stats(ip, len(domains))
            self.console.print_ip_complete(ip, len(domains))
