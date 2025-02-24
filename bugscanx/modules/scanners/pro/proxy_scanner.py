import socket
from .bug_scanner import BugScanner

class ProxyScanner(BugScanner):
    proxy_list = []
    port_list = []
    target = ''
    method = 'GET'
    path = '/'
    protocol = 'HTTP/1.1'
    payload = ''
    bug = ''

    def log_info(self, proxy_host_port, response_lines, color):
        CC = self.logger.special_chars['CC']
        color_code = self.logger.special_chars.get(color, '')
        status_code = response_lines[0].split(' ')[1] if response_lines and len(response_lines[0].split(' ')) > 1 else 'N/A'
        if status_code == 'N/A':
             return
        
        # Format the response lines with indentation and add extra newline
        formatted_response = '\n    '.join(response_lines)
        message = f"{color_code}{proxy_host_port.ljust(32)} {status_code}\n    {formatted_response}{CC}\n"
        super().log(message)

    def get_task_list(self):
        for proxy_host in self.filter_list(self.proxy_list):
            for port in self.filter_list(self.port_list):
                yield {
                    'proxy_host': proxy_host,
                    'port': port,
                }

    def init(self):
        super().init()
        self.log_info('Proxy:Port', ['Code'], 'G1')
        self.log_info('----------', ['----'], 'G1')
        self.log_replace("Initializing scan...")

    def task(self, payload):
        proxy_host = payload['proxy_host']
        port = payload['port']
        proxy_host_port = f"{proxy_host}:{port}"
        response_lines = []
        success = False

        formatted_payload = (
            self.payload
            .replace('[method]', self.method)
            .replace('[path]', self.path)
            .replace('[protocol]', self.protocol)
            .replace('[host]', self.target)
            .replace('[bug]', self.bug if self.bug else '')
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
                
                if response_lines and ' 101 ' in response_lines[0]:
                    success = True

        # except socket.timeout:
        #     response_lines = ['Timeout']
        # except ConnectionRefusedError:
        #     response_lines = ['Connection Refused']
        except Exception:
             pass
            # response_lines = [f'Error: {str(e)}']
        finally:
            if 'conn' in locals():
                conn.close()

        color = 'G1' if success else 'W2'
        self.log_info(proxy_host_port, response_lines, color)
        self.log_replace()
        
        if success:
            self.task_success({
                'proxy_host': proxy_host,
                'proxy_port': port,
                'response_lines': response_lines,
                'target': self.target
            })

