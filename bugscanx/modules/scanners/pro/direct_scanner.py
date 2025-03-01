import socket
from .bug_scanner import BugScanner

class DirectScanner(BugScanner):
    method_list = []
    host_list = []
    port_list = []

    def log_info(self, **kwargs):
        kwargs.setdefault('color', '')
        kwargs.setdefault('status_code', '')
        server = kwargs.get('server', '')
        kwargs['server'] = (server[:12] + "...") if len(server) > 12 else f"{server:<12}"
        kwargs.setdefault('ip', '')
        kwargs.setdefault('port', '')
        kwargs.setdefault('host', '')

        CC = '\033[0m'

        colors = {
            'method': '\033[94m',
            'status_code': '\033[92m',
            'server': '\033[93m',
            'port': '\033[95m',
            'ip': '\033[97m',
            'host': '\033[96m'
        }

        messages = [
            f'{colors["method"]}{{method:<6}}{CC}',
            f'{colors["status_code"]}{{status_code:<4}}{CC}',
            f'{colors["server"]}{{server:<15}}{CC}',
            f'{colors["port"]}{{port:<4}}{CC}',
            f'{colors["ip"]}{{ip:<16}}{CC}'
            f'{colors["host"]}{{host}}{CC}',
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
        self.log_replace("Scan completed")
        super().complete()