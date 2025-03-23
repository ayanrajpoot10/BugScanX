import time
import ipaddress
from threading import Lock
from .logger import console

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

def process_cidr(cidr):
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        console.print(f"[bold red] Invalid CIDR block {cidr}: {e}[/bold red]")
        return []

def process_input(input_str):
    if '/' in input_str:
        return process_cidr(input_str)
    else:
        return [input_str]

def process_file(file_path):
    ips = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                ips.extend(process_input(line.strip()))
        return ips
    except Exception as e:
        console.print(f"[bold red] Error reading file {file_path}: {e}[/bold red]")
        return []
