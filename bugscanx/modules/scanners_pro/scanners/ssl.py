import ssl
import socket
from .base import BaseScanner


class SSLScanner(BaseScanner):
    def __init__(
        self,
        host_list=None,
        is_cidr_input=False,
    ):
        super().__init__()
        self.host_list = host_list or []
        self.tls_version = ssl.PROTOCOL_TLS
        self.is_cidr_input = is_cidr_input

    def log_info(self, **kwargs):
        if self.is_cidr_input:
            messages = [
                self.logger.colorize('{tls_version:<8}', 'CYAN'),
                self.logger.colorize('{sni}', 'LGRAY'),
            ]
        else:
            messages = [
                self.logger.colorize('{tls_version:<8}', 'CYAN'),
                self.logger.colorize('{ip:<15}', 'YELLOW'),
                self.logger.colorize('{sni}', 'LGRAY'),
            ]
        self.logger.log('  '.join(messages).format(**kwargs))

    def generate_tasks(self):
        for host in self.filter_list(self.host_list):
            yield {
                'host': host,
            }

    def init(self):
        if self.is_cidr_input:
            self.log_info(tls_version='TLS', sni='SNI')
            self.log_info(tls_version='---', sni='---')
        else:
            self.log_info(tls_version='TLS', ip='IP', sni='SNI')
            self.log_info(tls_version='---', ip='--', sni='---')

    def resolve_ip(self, host):
        try:
            return socket.gethostbyname(host)
        except Exception:
            return "Unknown"

    def task(self, payload):
        sni = payload['host']

        if not sni:
            return

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_client:
                socket_client.settimeout(2)
                socket_client.connect((sni, 443))
                context = ssl.SSLContext(self.tls_version)
                with context.wrap_socket(
                    socket_client,
                    server_hostname=sni,
                    do_handshake_on_connect=True,
                ) as ssl_socket:
                    
                    # Create unified data dictionary for both saving and logging
                    data = {
                        'sni': sni,
                        'tls_version': ssl_socket.version()
                    }
                    
                    # Only resolve IP when not scanning CIDR
                    if not self.is_cidr_input:
                        data['ip'] = self.resolve_ip(sni)
                    
                    self.success(data)
                    self.log_info(**data)
        except Exception:
            pass

        self.log_progress(sni)

    def complete(self):
        self.log_progress(self.logger.colorize("Scan completed", "GREEN"))
