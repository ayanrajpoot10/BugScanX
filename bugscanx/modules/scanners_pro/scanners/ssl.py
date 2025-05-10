import ssl
import socket
from .base import BaseScanner

class SSLScanner(BaseScanner):
    host_list = []

    def __init__(self):
        super().__init__()
        self.tls_version = ssl.PROTOCOL_TLS

    TLS_VERSIONS = {
        'TLS 1.0': ssl.PROTOCOL_TLSv1,
        'TLS 1.1': ssl.PROTOCOL_TLSv1_1,
        'TLS 1.2': ssl.PROTOCOL_TLSv1_2,
        'TLS 1.3': ssl.PROTOCOL_TLS
    }

    def get_task_list(self):
        for host in self.filter_list(self.host_list):
            yield {
                'host': host,
            }

    def log_info(self, **kwargs):
        kwargs.setdefault('color', '')
        kwargs.setdefault('sni', '')
        kwargs.setdefault('tls_version', '')
        
        messages = [
            self.colorize('{tls_version:<8}', 'CYAN'),
            self.colorize('{sni}', 'LGRAY'),
        ]
        super().log('  '.join(messages).format(**kwargs))

    def log_info_result(self, **kwargs):
        self.log_info(**kwargs)

    def init(self):
        super().init()
        self.log_info(tls_version='TLS', sni='SNI')
        self.log_info(tls_version='---', sni='---')

    def task(self, payload):
        sni = payload['host']

        if not sni:
            return

        response = {
            'sni': sni,
            'tls_version': 'Unknown'
        }

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_client:
                socket_client.settimeout(5)
                socket_client.connect((sni, 443))
                context = ssl.SSLContext(self.tls_version)
                with context.wrap_socket(
                    socket_client, server_hostname=sni, do_handshake_on_connect=True
                ) as ssl_socket:
                    response['tls_version'] = ssl_socket.version()
                    self.task_success(sni)
                    self.log_info_result(**response)
        except Exception:
            pass

        self.log_replace(sni)

    def complete(self):
        self.log_replace(self.colorize("Scan completed", "GREEN"))
        super().complete()
