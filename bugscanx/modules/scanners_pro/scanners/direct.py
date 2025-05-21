import socket
import requests
import urllib3
from .base import BaseScanner
from bugscanx.utils.config import EXCLUDE_LOCATIONS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DirectScanner(BaseScanner):
    requests = requests
    DEFAULT_TIMEOUT = 3
    DEFAULT_RETRY = 1

    def __init__(
            self,
            method_list=None,
            host_list=None,
            port_list=None,
            no302=False,
            is_cidr_input=False
        ):
        super().__init__()
        self.method_list = method_list or []
        self.host_list = host_list or []
        self.port_list = port_list or []
        self.no302 = no302
        self.is_cidr_input = is_cidr_input

    def request(self, method, url, **kwargs):
        method = method.upper()
        kwargs['timeout'] = self.DEFAULT_TIMEOUT
        max_attempts = self.DEFAULT_RETRY

        for attempt in range(max_attempts):
            self.log_progress(method, url)
            try:
                return self.requests.request(method, url, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException
            ) as e:
                wait_time = (1 if isinstance(e, requests.exceptions.ConnectionError)
                           else 3)
                for _ in self.sleep(wait_time):
                    self.log_progress(method, url)
                if attempt == max_attempts - 1:
                    return None
        return None

    def log_info(self, **kwargs):
        server = kwargs.get('server', '')
        kwargs['server'] = ((server[:12] + "...") if len(server) > 12 
                          else f"{server:<12}")

        if self.is_cidr_input:
            messages = [
                self.logger.colorize(f"{{method:<6}}", "CYAN"),
                self.logger.colorize(f"{{status_code:<4}}", "GREEN"),
                self.logger.colorize(f"{{server:<15}}", "MAGENTA"),
                self.logger.colorize(f"{{port:<4}}", "ORANGE"),
                self.logger.colorize(f"{{host}}", "LGRAY")
            ]
        else:
            messages = [
                self.logger.colorize(f"{{method:<6}}", "CYAN"),
                self.logger.colorize(f"{{status_code:<4}}", "GREEN"),
                self.logger.colorize(f"{{server:<15}}", "MAGENTA"),
                self.logger.colorize(f"{{port:<4}}", "ORANGE"),
                self.logger.colorize(f"{{ip:<16}}", "BLUE"),
                self.logger.colorize(f"{{host}}", "LGRAY")
            ]

        self.logger.log('  '.join(messages).format(**kwargs))

    def generate_tasks(self):
        for method in self.filter_list(self.method_list):
            for host in self.filter_list(self.host_list):
                for port in self.filter_list(self.port_list):
                    yield {
                        'method': method.upper(),
                        'host': host,
                        'port': port,
                    }

    def init(self):
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

        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            return

        response = self.request(method, self.get_url(host, port), verify=False, allow_redirects=False)

        if response is None:
            return

        if self.no302 and response.status_code == 302:
            return

        if not self.no302:
            location = response.headers.get('location', '')
            if location and location in EXCLUDE_LOCATIONS:
                return

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

        self.success(data)
        self.log_info(**data)

    def complete(self):
        self.log_progress(self.logger.colorize("Scan completed", "GREEN"))
