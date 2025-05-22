import time
import ipaddress
import random
from threading import Lock

import requests

from bugscanx.utils.http import HEADERS, USER_AGENTS


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


class RequestHandler:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        self.rate_limiter = RateLimiter(1.0)

    def _get_headers(self):
        headers = HEADERS.copy()
        headers["user-agent"] = random.choice(USER_AGENTS)
        return headers

    def get(self, url, timeout=10):
        self.rate_limiter.acquire()
        try:
            response = self.session.get(url, timeout=timeout, headers=self._get_headers())
            if response.status_code == 200:
                return response
        except requests.RequestException:
            pass
        return None

    def post(self, url, data=None):
        self.rate_limiter.acquire()
        try:
            response = self.session.post(url, data=data, headers=self._get_headers())
            if response.status_code == 200:
                return response
        except requests.RequestException:
            pass
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class CursorManager:
    def __enter__(self):
        print('\033[?25l', end='', flush=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('\033[?25h', end='', flush=True)


def process_cidr(cidr):
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
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
        return []
