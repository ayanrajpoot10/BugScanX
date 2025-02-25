import socket
from .bug_scanner import BugScanner

class DirectScanner(BugScanner):
    method_list = []
    host_list = []
    port_list = []

    def log_info(self, **kwargs):
        kwargs.setdefault('color', '')
        kwargs.setdefault('status_code', '')
        kwargs.setdefault('server', '')
        kwargs.setdefault('ip', '')

        CC = self.logger.special_chars['CC']
        kwargs['CC'] = CC

        colors = {
            'status_code': '\033[92m',
            'server': '\033[93m',
            'port': '\033[95m',
            'host': '\033[96m',
            'ip': '\033[97m'
        }

        messages = [
            f'{colors["status_code"]}{{status_code:<4}}{CC}',
            f'{colors["server"]}{{server:<22}}{CC}',
            f'{colors["port"]}{{port:<4}}{CC}',
            f'{colors["host"]}{{host:<20}}{CC}',
            f'{colors["ip"]}{{ip}}{CC}'
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
        self.log_info(status_code='Code', server='Server', port='Port', host='Host', ip='IP')
        self.log_info(status_code='----', server='------', port='----', host='----', ip='--')

    def task(self, payload):
        method = payload['method']
        host = payload['host']
        port = payload['port']

        if not host:
            return

        try:
            response = self.request(method, self.get_url(host, port), retry=1, timeout=3, allow_redirects=False)
        except Exception:
            return

        if response:
            location = response.headers.get('location', '')
            if location and location.startswith("https://jio.com/BalanceExhaust"):
                return

            try:
                ip = socket.gethostbyname(host)
            except socket.gaierror:
                ip = 'N/A'

            data = {
                'host': host,
                'port': port,
                'status_code': response.status_code,
                'server': response.headers.get('server', ''),
                'location': location,
                'ip': ip
            }

            self.task_success(data)
            self.log_info(**data)