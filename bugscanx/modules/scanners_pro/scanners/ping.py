import socket
from .base import BaseScanner


class PingScanner(BaseScanner):
    def __init__(
        self,
        host_list=None,
        port_list=None,
        is_cidr_input=False,
    ):
        super().__init__()
        self.host_list = host_list or []
        self.port_list = port_list or []
        self.is_cidr_input = is_cidr_input

    def log_info(self, **kwargs):
        if self.is_cidr_input:
            log_parts = [
                self.logger.colorize('{port:<6}', 'CYAN'),
                self.logger.colorize('{host}', 'LGRAY'),
            ]
        else:
            log_parts = [
                self.logger.colorize('{port:<6}', 'CYAN'),
                self.logger.colorize('{ip:<15}', 'YELLOW'),
                self.logger.colorize('{host}', 'LGRAY'),
            ]

        self.logger.log('  '.join(log_parts).format(**kwargs))

    def generate_tasks(self):
        for host in self.filter_list(self.host_list):
            for port in self.filter_list(self.port_list):
                yield {
                    'host': host,
                    'port': port,
                }

    def init(self):
        if self.is_cidr_input:
            self.log_info(port='Port', host='Host')
            self.log_info(port='----', host='----')
        else:
            self.log_info(port='Port', ip='IP', host='Host')
            self.log_info(port='----', ip='--', host='----')

    def resolve_ip(self, host):
        try:
            return socket.gethostbyname(host)
        except Exception:
            return "Unknown"

    def task(self, payload):
        host = payload['host']
        port = payload['port']

        if not host:
            return
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex((host, int(port)))

            if result == 0:
                data = {
                    'host': host,
                    'port': port
                }
                
                # Only resolve IP when not scanning CIDR
                if not self.is_cidr_input:
                    ip = self.resolve_ip(host)
                    data['ip'] = ip
                
                self.success(data)
                self.log_info(**data)

        except Exception:
            pass

        self.log_progress(f"{host}:{port}")

    def complete(self):
        self.log_progress(self.logger.colorize("Scan completed", "GREEN"))
