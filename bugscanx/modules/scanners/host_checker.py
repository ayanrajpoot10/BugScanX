import os
import ssl
import sys
import socket
import multithreading
from bugscanx.utils import *

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

class ProxyScanner(DirectScanner):
	proxy = []

	def log_replace(self, *args):
		super().log_replace(':'.join(self.proxy), *args)

	def request(self, *args, **kwargs):
		proxy = self.get_url(self.proxy[0], self.proxy[1])

		return super().request(*args, proxies={'http': proxy, 'https': proxy}, **kwargs)

	def task(self, payload):
		method = payload['method']
		host = payload['host']
		port = payload['port']

		if not host:
			return

		super().task(payload)

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
	filename = get_input(prompt="\n Enter the filename",validator=file_path_validator,completer=completer)
	mode = create_prompt("list", " Enter the mode", "selection", choices=["direct", "proxy", "ssl", "udp"])
	#mode = get_input(prompt=" Enter the mode (direct, proxy, ssl)",default="direct",validator=not_empty_validator)
	method_list = ""
	port_list = get_input(prompt=" Enter the port list",default="80",validator=digit_validator)
	proxy = ""
	output = get_input(prompt=" Enter the output file name",default=f"result_{os.path.basename(filename)}",validator=not_empty_validator)
	threads = get_input(prompt=" Enter the number of threads",default= "50",validator=digit_validator)

	if mode == 'direct':
		method_list = create_prompt("list", " Enter the method list", "selection", choices=["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH"])
		#method_list = get_input(prompt=" Enter the method list (comma-separated)",default="HEAD",validator=not_empty_validator)
	elif mode == 'proxy':
		proxy = get_input(prompt=" Enter the proxy (host:port)",validator=not_empty_validator)

	return {
		'filename': filename,
		'mode': mode,
		'method_list': method_list,
		'port_list': port_list,
		'proxy': proxy,
		'output': output,
		'threads': threads,
	}

def main():
	user_input = get_user_input()

	method_list = user_input['method_list'].split(',')
	host_list = read_hosts(user_input['filename'])
	port_list = user_input['port_list'].split(',')
	proxy = user_input['proxy'].split(':')

	if user_input['mode'] == 'direct':
		scanner = DirectScanner()

	elif user_input['mode'] == 'ssl':
		scanner = SSLScanner()

	elif user_input['mode'] == 'proxy':
		if not proxy or len(proxy) != 2:
			sys.exit('--proxy host:port')

		scanner = ProxyScanner()
		scanner.proxy = proxy

	elif user_input['mode'] == 'udp':
		scanner = UdpScanner()
		scanner.udp_server_host = 'bugscanner.tppreborn.my.id'
		scanner.udp_server_port = '8853'

	else:
		sys.exit('Not Available!')

	scanner.method_list = method_list
	scanner.host_list = host_list
	scanner.port_list = port_list
	scanner.threads = int(user_input['threads'])
	scanner.start()

	if user_input['output']:
		with open(user_input['output'], 'w+') as file:
			file.write('\n'.join([str(x) for x in scanner.success_list()]) + '\n')

