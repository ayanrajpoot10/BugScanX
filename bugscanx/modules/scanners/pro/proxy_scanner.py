import socket
from .bug_scanner import BugScanner

class ProxyScanner(BugScanner):
    
    host_list = []
    port_list = []
    target = ''
    method = 'GET'
    path = '/'
    protocol = 'HTTP/1.1'
    payload = ''
    bug = ''

    def log_info(self, proxy_host_port, response_lines, color):
        status_code = response_lines[0].split(' ')[1] if response_lines and len(response_lines[0].split(' ')) > 1 else 'N/A'
        if status_code == 'N/A' or status_code == '302':
             return
        
        color_name = 'GREEN' if color == 'G1' else 'GRAY'
        formatted_response = '\n    '.join(response_lines)
        message = f"{self.colorize(proxy_host_port.ljust(32) + ' ' + status_code, color_name)}\n"
        message += f"{self.colorize('    ' + formatted_response, color_name)}\n"
        super().log(message)

    def get_task_list(self):
        for proxy_host in self.filter_list(self.host_list):
            for port in self.filter_list(self.port_list):
                yield {
                    'proxy_host': proxy_host,
                    'port': port,
                }

    def init(self):
        super().init()
        self.log("\n")
        self.log_info('Proxy:Port', ['Code'], 'G1')
        self.log_info('----------', ['----'], 'G1')

    def task(self, payload):
        proxy_host = payload['proxy_host']
        port = payload['port']
        proxy_host_port = f"{proxy_host}:{port}"
        response_lines = []
        success = False

        self.log_replace(f"{proxy_host}")

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

        except Exception:
             pass
        finally:
            if 'conn' in locals():
                conn.close()

        color = 'G1' if success else 'W2'
        self.log_info(proxy_host_port, response_lines, color)
        self.log_replace(f"{proxy_host}")
        
        if success:
            self.task_success({
                'proxy_host': proxy_host,
                'proxy_port': port,
                'response_lines': response_lines,
                'target': self.target
            })

    def complete(self):
        self.log_replace(self.colorize("Scan completed", "green"))
        super().complete()
