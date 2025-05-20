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
        self._setup_session()
        self.rate_limiter = RateLimiter(1.0)

    def _setup_session(self):
        self.session.headers.update(HEADERS)
        self.session.timeout = 10

    def get(self, url):
        self.rate_limiter.acquire()
        try:
            self.session.headers["user-agent"] = random.choice(USER_AGENTS)
            response = self.session.get(url)
            if response.status_code == 200:
                return response
        except requests.RequestException:
            pass
        return None

    def post(self, url, data=None):
        self.rate_limiter.acquire()
        try:
            self.session.headers["user-agent"] = random.choice(USER_AGENTS)
            response = self.session.post(url, data=data)
            if response.status_code == 200:
                return response
        except requests.RequestException:
            pass
        return None

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


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
