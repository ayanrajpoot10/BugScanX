import socket
from .base import BaseScanner


class ProxyScanner(BaseScanner):
    def __init__(
        self,
        host_list=None,
        port_list=None,
        target='',
        payload='',
    ):
        super().__init__()
        self.host_list = host_list or []
        self.port_list = port_list or []
        self.target = target
        self.payload = payload

    def log_info(self, proxy_host_port, status_code, response_lines=None):
        if response_lines is None:
            response_lines = []
            
        if not response_lines and status_code in ['N/A', '302']:
            return

        color_name = 'GREEN' if status_code == '101' else 'GRAY'
        formatted_response = '\n    '.join(response_lines)
        message = (
            f"{self.logger.colorize(proxy_host_port.ljust(32) + ' ' + status_code, color_name)}\n"
        )
        if formatted_response:
            message += f"{self.logger.colorize('    ' + formatted_response, color_name)}\n"
        self.logger.log(message)

    def generate_tasks(self):
        for proxy_host in self.filter_list(self.host_list):
            for port in self.filter_list(self.port_list):
                yield {
                    'proxy_host': proxy_host,
                    'port': port,
                }

    def init(self):
        self.log_info(proxy_host_port='Proxy:Port', status_code='Code')
        self.log_info(proxy_host_port='----------', status_code='----')

    def task(self, payload):
        proxy_host = payload['proxy_host']
        port = payload['port']
        proxy_host_port = f"{proxy_host}:{port}"
        response_lines = []

        formatted_payload = (
            self.payload
            .replace('[host]', self.target)
            .replace('[crlf]', '\r\n')
            .replace('[cr]', '\r')
            .replace('[lf]', '\n')
        )

        try:
            with socket.create_connection((proxy_host, int(port)), timeout=3) as conn:
                conn.sendall(formatted_payload.encode())
                conn.settimeout(3)
                data = b''
                while True:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    data += chunk
                    if b'\r\n\r\n' in data:
                        break

                response = data.decode(errors='ignore').split('\r\n\r\n')[0]
                response_lines = [line.strip() for line in response.split('\r\n') if line.strip()]

                status_code = response_lines[0].split(' ')[1] if response_lines and len(response_lines[0].split(' ')) > 1 else 'N/A'
                if status_code not in ['N/A', '302']:
                    self.log_info(proxy_host_port, status_code, response_lines)
                    self.success({
                        'proxy_host': proxy_host,
                        'proxy_port': port,
                        'response_lines': response_lines,
                        'target': self.target,
                        'status_code': status_code
                    })

        except Exception:
            pass
        finally:
            if 'conn' in locals():
                conn.close()

        self.log_progress(f"{proxy_host}")

    def complete(self):
        self.log_progress(self.logger.colorize("Scan completed", "GREEN"))
