from .direct_scanner import DirectScanner
import socket

class CustomDirectScanner(DirectScanner):
    def task(self, payload):
        method = payload['method']
        host = payload['host']
        port = payload['port']

        response = self.request(method, self.get_url(host, port), verify=False, allow_redirects=False)

        if response is None:
            self.task_failed(payload)
            return

        if response.status_code == 302:
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
            'ip': ip
        }

        self.task_success(data)
        self.log_info(**data)
    
    def complete(self):
        self.log_replace(self.colorize("Scan completed", "GREEN"))
        super().complete()
