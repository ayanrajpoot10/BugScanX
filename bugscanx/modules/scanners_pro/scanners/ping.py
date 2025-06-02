import socket
from .base import BaseScanner


class PingScannerBase(BaseScanner):
    def __init__(
        self,
        port_list=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.port_list = port_list or []

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
                
                self._handle_success(data)

        except Exception:
            pass

        self.log_progress(f"{host}:{port}")

    def complete(self):
        self.log_progress(self.logger.colorize("Scan completed", "GREEN"))


class HostPingScanner(PingScannerBase):    
    def __init__(
        self,
        input_file=None,
        port_list=None,
        threads=50,
        **kwargs
    ):
        super().__init__(port_list=port_list, threads=threads, is_cidr_input=False, **kwargs)
        self.input_file = input_file

        if self.input_file:
            self.set_host_total(self.input_file)
        
    def init(self):
        self.log_info(port='Port', ip='IP', host='Host')
        self.log_info(port='----', ip='--', host='----')

    def log_info(self, **kwargs):
        log_parts = [
            self.logger.colorize('{port:<6}', 'CYAN'),
            self.logger.colorize('{ip:<15}', 'YELLOW'),
            self.logger.colorize('{host}', 'LGRAY'),
        ]

        self.logger.log('  '.join(log_parts).format(**kwargs))

    def _handle_success(self, data):
        ip = self.resolve_ip(data['host'])
        data['ip'] = ip
        self.success(data)
        self.log_info(**data)
        
    def generate_tasks(self):
        for host in self.generate_hosts_from_file(self.input_file):
            for port in self.port_list:
                yield {
                    'host': host,
                    'port': port,
                }


class CIDRPingScanner(PingScannerBase):    
    def __init__(
        self,
        cidr_ranges=None,
        port_list=None,
        threads=50,
        **kwargs
    ):
        super().__init__(port_list=port_list, threads=threads, is_cidr_input=True, cidr_ranges=cidr_ranges, **kwargs)
        self.cidr_ranges = cidr_ranges or []
        
        if self.cidr_ranges:
            self.set_cidr_total(self.cidr_ranges)

    def log_info(self, **kwargs):
        log_parts = [
            self.logger.colorize('{port:<6}', 'CYAN'),
            self.logger.colorize('{host}', 'LGRAY'),
        ]

        self.logger.log('  '.join(log_parts).format(**kwargs))

    def _handle_success(self, data):
        self.success(data)
        self.log_info(**data)

    def generate_tasks(self):
        for host in self.generate_cidr_hosts(self.cidr_ranges):
            for port in self.port_list:
                yield {
                    'host': host,
                    'port': port,
                }

    def init(self):
        self.log_info(port='Port', host='Host')
        self.log_info(port='----', host='----')
