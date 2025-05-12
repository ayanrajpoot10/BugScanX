import socket
import requests
import urllib3
from itertools import product
from .base import BaseScanner
from bugscanx.utils.config import EXCLUDE_LOCATIONS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DirectScanner(BaseScanner):
    method_list = []
    host_list = []
    port_list = []
    requests = requests
    DEFAULT_TIMEOUT = 3
    DEFAULT_RETRY = 1
    no302 = False
    is_cidr_input = False

    def request(self, method, url, **kwargs):
        method = method.upper()
        kwargs['timeout'] = self.DEFAULT_TIMEOUT
        max_attempts = self.DEFAULT_RETRY
        
        for attempt in range(max_attempts):
            self.log_replace(method, url)
            try:
                return self.requests.request(method, url, **kwargs)
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.Timeout) as e:
                wait_time = 1 if isinstance(e, requests.exceptions.ConnectionError) else 5
                for _ in self.sleep(wait_time):
                    self.log_replace(method, url)
                if attempt == max_attempts - 1:
                    return None
        return None

    def log_info(self, **kwargs):
        kwargs.setdefault('color', '')
        kwargs.setdefault('status_code', '')
        server = kwargs.get('server', '')
        kwargs['server'] = (server[:12] + "...") if len(server) > 12 else f"{server:<12}"
        kwargs.setdefault('ip', '')
        kwargs.setdefault('port', '')
        kwargs.setdefault('host', '')

        if self.is_cidr_input:
            messages = [
                self.colorize(f"{{method:<6}}", "CYAN"),
                self.colorize(f"{{status_code:<4}}", "GREEN"),
                self.colorize(f"{{server:<15}}", "MAGENTA"),
                self.colorize(f"{{port:<4}}", "ORANGE"),
                self.colorize(f"{{host}}", "LGRAY")
            ]
        else:
            messages = [
                self.colorize(f"{{method:<6}}", "CYAN"),
                self.colorize(f"{{status_code:<4}}", "GREEN"),
                self.colorize(f"{{server:<15}}", "MAGENTA"),
                self.colorize(f"{{port:<4}}", "ORANGE"),
                self.colorize(f"{{ip:<16}}", "BLUE"),
                self.colorize(f"{{host}}", "LGRAY")
            ]

        super().log('  '.join(messages).format(**kwargs))

    def get_task_list(self):
        methods = self.filter_list(self.method_list)
        hosts = self.filter_list(self.host_list)
        ports = self.filter_list(self.port_list)
        for m, h, p in product(methods, hosts, ports):
            yield {'method': m.upper(), 'host': h, 'port': p}

    def init(self):
        super().init()
        if self.is_cidr_input:
            self.log_info(method='Method', status_code='Code', server='Server', port='Port', host='Host')
            self.log_info(method='------', status_code='----', server='------', port='----', host='----')
        else:
            self.log_info(method='Method', status_code='Code', server='Server', port='Port', ip='IP', host='Host')
            self.log_info(method='------', status_code='----', server='------', port='----', ip='--', host='----')

    def task(self, payload):
        method = payload['method']
        host = payload['host']
        port = payload['port']

        response = self.request(method, self.get_url(host, port), verify=False, allow_redirects=False)

        if response is None:
            return

        if self.no302 and response.status_code == 302:
            return

        if not self.no302:
            location = response.headers.get('location', '')
            if location and location in EXCLUDE_LOCATIONS:
                return

        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            ip = 'N/A'

        data = {
            'method': method,
            'host': host,
            'port': port,
            'status_code': response.status_code,
            'server': response.headers.get('server', ''),
            'ip': ip
        }

        if not self.no302:
            data['location'] = response.headers.get('location', '')

        self.task_success(data)
        self.log_info(**data)

    def complete(self):
        self.log_replace(self.colorize("Scan completed", "GREEN"))
        super().complete()
