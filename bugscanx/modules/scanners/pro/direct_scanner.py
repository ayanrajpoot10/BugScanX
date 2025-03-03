import socket
import requests
from .bug_scanner import BugScanner

class DirectScanner(BugScanner):
    method_list = []
    host_list = []
    port_list = []
    requests = requests

    def request_connection_error(self, method, url, **_):
        for _ in self.sleep(1):
            self.log_replace(method, url, 'connection error')
        return 1

    def request_read_timeout(self, method, url, **_):
        for remains in self.sleep(10):
            self.log_replace(method, url, 'read timeout', remains)
        return 1

    def request_timeout(self, method, url, **_):
        for remains in self.sleep(5):
            self.log_replace(method, url, 'timeout', remains)
        return 1

    def request(self, method, url, **kwargs):
        method = method.upper()

        kwargs['timeout'] = kwargs.get('timeout', 5)

        retry = int(kwargs.pop('retry', 5))

        while retry > 0:
            self.log_replace(method, url)

            try:
                return self.requests.request(method, url, **kwargs)

            except requests.exceptions.ConnectionError:
                retry_decrease = self.request_connection_error(method, url, **kwargs)
                retry -= retry_decrease or 0

            except requests.exceptions.ReadTimeout:
                retry_decrease = self.request_read_timeout(method, url, **kwargs)
                retry -= retry_decrease or 0

            except requests.exceptions.Timeout:
                retry_decrease = self.request_timeout(method, url, **kwargs)
                retry -= retry_decrease or 0

        return None

    def log_info(self, **kwargs):
        kwargs.setdefault('color', '')
        kwargs.setdefault('status_code', '')
        server = kwargs.get('server', '')
        kwargs['server'] = (server[:12] + "...") if len(server) > 12 else f"{server:<12}"
        kwargs.setdefault('ip', '')
        kwargs.setdefault('port', '')
        kwargs.setdefault('host', '')

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
        for method in self.filter_list(self.method_list):
            for host in self.filter_list(self.host_list):
                for port in self.filter_list(self.port_list):
                    yield {
                        'method': method.upper(),
                        'host': host,
                        'port': port,
                    }

    def init(self):
        super().init()
        self.log_info(method='Method', status_code='Code', server='Server', port='Port', ip='IP', host='Host')
        self.log_info(method='------', status_code='----', server='------', port='----', ip='--', host='----')

    def task(self, payload):
        method = payload['method']
        host = payload['host']
        port = payload['port']

        response = self.request(method, self.get_url(host, port), retry=1, timeout=3, allow_redirects=False, verify=False)

        if response is None:
            self.task_failed(payload)
            return

        location = response.headers.get('location', '')
        if location and location.startswith("https://jio.com/BalanceExhaust"):
            self.task_failed(payload)
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
            'location': location,
            'ip': ip
        }

        self.task_success(data)
        self.log_info(**data)

    def complete(self):
        self.log_replace(self.colorize("Scan completed", "GREEN"))
        super().complete()