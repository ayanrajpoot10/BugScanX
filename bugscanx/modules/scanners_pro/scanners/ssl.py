import ssl
import socket
from .base import BaseScanner


class SSLScanner(BaseScanner):
    def __init__(
        self,
        host_list=None,
    ):
        super().__init__()
        self.host_list = host_list or []
        self.tls_version = ssl.PROTOCOL_TLS

    def log_info(self, **kwargs):
        messages = [
            self.logger.colorize('{tls_version:<8}', 'CYAN'),
            self.logger.colorize('{sni}', 'LGRAY'),
        ]
        self.logger.log('  '.join(messages).format(**kwargs))

    def generate_tasks(self):
        for host in self.filter_list(self.host_list):
            yield {
                'host': host,
            }

    def init(self):
        self.log_info(tls_version='TLS', sni='SNI')
        self.log_info(tls_version='---',sni='---')

    def task(self, payload):
        sni = payload['host']

        if not sni:
            return

        response = {
            'sni': sni,
            'tls_version': 'Unknown',
        }

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
                    response['tls_version'] = ssl_socket.version()
                    self.success(sni)
                    self.log_info(**response)
        except Exception:
            pass

        self.log_progress(sni)

    def complete(self):
        self.log_progress(self.logger.colorize("Scan completed", "GREEN"))
