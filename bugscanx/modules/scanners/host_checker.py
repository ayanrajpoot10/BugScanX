import json
import os
import socket
import ssl
import sys

import multithreading

from bugscanx.utils import (
     get_input,
     create_prompt,
     digit_validator,
     file_path_validator,
     not_empty_validator,
     completer
)

class BugScanner(multithreading.MultiThreadRequest):
	threads: int

	def request_connection_error(self, *args, **kwargs):
		return 1

	def request_read_timeout(self, *args, **kwargs):
		return 1

	def request_timeout(self, *args, **kwargs):
		return 1

	def convert_host_port(self, host, port):
		return host + (f':{port}' if bool(port not in ['80', '443']) else '')

	def get_url(self, host, port, uri=None):
		port = str(port)
		protocol = 'https' if port == '443' else 'http'

		return f'{protocol}://{self.convert_host_port(host, port)}' + (f'/{uri}' if uri is not None else '')

	def init(self):
		self._threads = self.threads or self._threads

	def complete(self):
		pass

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
            'method': '\033[94m',
            'status_code': '\033[92m',
            'server': '\033[93m',
            'port': '\033[95m',
            'host': '\033[96m',
            'ip': '\033[97m'
        }

        messages = [
            f'{colors["method"]}{{method:<6}}{CC}',
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
        self.log_info(method='Method', status_code='Code', server='Server', port='Port', host='Host', ip='IP')
        self.log_info(method='------', status_code='----', server='------', port='----', host='----', ip='--')

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
                'method': method,
                'host': host,
                'port': port,
                'status_code': response.status_code,
                'server': response.headers.get('server', ''),
                'location': location,
                'ip': ip
            }

            self.task_success(data)
            self.log_info(**data)

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
        message = f"{color_code}{proxy_host_port.ljust(32)} {status_code} {' -- '.join(response_lines)}{CC}"
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
        self.log_replace(f"Scanned: {self._task_list_scanned_total}/{self._task_list_total}")
        
        if success:
            self.task_success({
                'proxy_host': proxy_host,
                'proxy_port': port,
                'response_lines': response_lines,
                'target': self.target
            })


class SSLScanner(BugScanner):
	host_list = []

	def get_task_list(self):
		for host in self.filter_list(self.host_list):
			yield {
				'host': host,
			}

	def log_info(self, color, status, server_name_indication):
		super().log(f'{color}{status:<6}  {server_name_indication}')

	def log_info_result(self, **kwargs):
		G1 = self.logger.special_chars['G1']
		W2 = self.logger.special_chars['W2']

		status = kwargs.get('status', '')
		status = 'True' if status else ''
		server_name_indication = kwargs.get('server_name_indication', '')

		color = G1 if status else W2

		self.log_info(color, status, server_name_indication)

	def init(self):
		super().init()

		self.log_info('', 'Status', 'Server Name Indication')
		self.log_info('', '------', '----------------------')

	def task(self, payload):
		server_name_indication = payload['host']

		if not server_name_indication:
			return

		self.log_replace(server_name_indication)

		response = {
			'server_name_indication': server_name_indication,
		}

		try:
			socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			socket_client.settimeout(5)
			socket_client.connect(("77.88.8.8", 443))
			socket_client = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(
				socket_client, server_hostname=server_name_indication, do_handshake_on_connect=True
			)
			response['status'] = True

			self.task_success(server_name_indication)

		except Exception:
			response['status'] = False

		self.log_info_result(**response)

class UdpScanner(BugScanner):
	udp_server_host: str
	udp_server_port: int

	host_list: list

	def get_task_list(self):
		for host in self.host_list:
			yield {
				'host': host,
			}

	def log_info(self, color, status, hostname):
		super().log(f'{color}{status:<6}  {hostname}')

	def init(self):
		super().init()

		self.log_info('', 'Status', 'Host')
		self.log_info('', '------', '----')

	def task(self, payload):
		host = payload['host']

		if not host:
			return

		self.log_replace(host)

		bug = f'{host}.{self.udp_server_host}'

		G1 = self.logger.special_chars['G1']
		W2 = self.logger.special_chars['W2']

		try:
			client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

			client.settimeout(3)
			client.sendto(bug.encode(), (bug, int(self.udp_server_port)))
			client.recv(4)

			client.settimeout(5)
			client.sendto(bug.encode(), (bug, int(self.udp_server_port)))
			client.recv(4)

			client.settimeout(5)
			client.sendto(bug.encode(), (bug, int(self.udp_server_port)))
			client.recv(4)

			self.log_info(G1, 'True', host)

			self.task_success(host)

		except (OSError, socket.timeout):
			self.log_info(W2, '', host)

		finally:
			client.close()

def read_hosts(filename):
    with open(filename) as file:
        for line in file:
            yield line.strip()

def get_user_input():
    mode = create_prompt("list", " Select the mode", "selection", choices=["direct", "proxy", "ssl", "udp"])
    if mode == 'direct':
        filename = get_input(" Enter the filename", validator=file_path_validator, completer=completer)
        port_list = get_input(" Enter the port list", default="80", validator=digit_validator)
        output = get_input(" Enter the output file name",default=f"result_{os.path.basename(filename)}", validator=not_empty_validator)
        threads = get_input(" Enter the number of threads", default= "50", validator=digit_validator)
        method_list = create_prompt("list", " select the http method", "selection", choices=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"])
        return{
            'filename': filename,
            'method_list': method_list,
            'port_list': port_list,
            'output': output,
            'threads': threads,
            'mode': mode
        }
    elif mode == 'proxy':
        proxy_file = get_input(" Enter the file name of proxy file", validator=file_path_validator, completer=completer)
        target_url = get_input(" Enter target url", default="in1.wstunnel.site")
        method = get_input(" Enter HTTP method", default="GET")
        path = get_input(" Enter path", default="/")
        protocol = get_input(" Enter protocol", default="HTTP/1.1")
        # Default payload includes WebSocket handshake headers
        default_payload = (
            "[method] [path] [protocol][crlf]"
            "Host: [host][crlf]"
            "Connection: Upgrade[crlf]"
            "Upgrade: websocket[crlf][crlf]"
        )
        payload = get_input(" Enter payload", default=default_payload)
        port_list = get_input(" Enter the port list", default="80", validator=digit_validator)
        output = get_input(" Enter the output file name", default=f"result_{os.path.basename(proxy_file)}", validator=not_empty_validator)
        threads = get_input(" Enter the number of threads", default="50", validator=digit_validator)
        bug = get_input(" Enter bug (optional)", default="")
        return {
            'proxy_file': proxy_file,
            'output': output,
            'threads': threads,
            'target_url': target_url,
            'method': method,
            'path': path,
            'protocol': protocol,
            'bug': bug,
            'payload': payload,
            'port_list': port_list,
            'mode': mode
        }

    elif mode == 'ssl':
        filename = get_input(" Enter the filename", validator=file_path_validator, completer=completer)
        output = get_input(" Enter the output file name",default=f"result_{os.path.basename(filename)}", validator=not_empty_validator)
        threads = get_input(" Enter the number of threads", default= "50", validator=digit_validator)
        return{
            'filename': filename,
            'output': output,
            'threads': threads,
            'mode': mode
        }
    
    elif mode == 'udp':
        filename = get_input(" Enter the filename", validator=file_path_validator, completer=completer)
        output = get_input(" Enter the output file name",default=f"result_{os.path.basename(filename)}", validator=not_empty_validator)
        threads = get_input(" Enter the number of threads", default= "50", validator=digit_validator)
        return{
            'filename': filename,
            'output': output,
            'threads': threads,
            'mode': mode
        }

def main():
    user_input = get_user_input()

    if user_input['mode'] == 'direct':
        method_list = user_input['method_list'].split(',')
        host_list = read_hosts(user_input['filename'])
        port_list = user_input['port_list'].split(',')

        scanner = DirectScanner()
        scanner.method_list = method_list
        scanner.host_list = host_list
        scanner.port_list = port_list

    elif user_input['mode'] == 'proxy':
        proxy_list = list(read_hosts(user_input['proxy_file']))
        port_list = user_input['port_list'].split(',')

        scanner = ProxyScanner()
        scanner.proxy_list = proxy_list
        scanner.target = user_input['target_url']
        scanner.method = user_input['method']
        scanner.path = user_input['path']
        scanner.protocol = user_input['protocol']
        scanner.bug = user_input['bug']
        scanner.payload = user_input['payload']
        scanner.port_list = port_list

    elif user_input['mode'] == 'ssl':
        host_list = read_hosts(user_input['filename'])

        scanner = SSLScanner()
        scanner.host_list = host_list


    elif user_input['mode'] == 'udp':
        host_list = read_hosts(user_input['filename'])
        scanner = UdpScanner()
        scanner.host_list = host_list
        scanner.udp_server_host = 'bugscanner.tppreborn.my.id'
        scanner.udp_server_port = '8853'

    else:
        sys.exit('Not Available!')

    scanner.threads = int(user_input['threads'])
    scanner.start()

    if user_input['output']:
        with open(user_input['output'], 'w+') as file:
            if user_input['mode'] == 'proxy':
                json.dump(scanner.success_list(), file, indent=2)
            else:
                file.write('\n'.join([str(x) for x in scanner.success_list()]) + '\n')
