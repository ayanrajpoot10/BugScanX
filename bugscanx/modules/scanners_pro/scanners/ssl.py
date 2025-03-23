import ssl
import socket
from .base import BaseScanner

class SSLScanner(BaseScanner):
	host_list = []

	def get_task_list(self):
		for host in self.filter_list(self.host_list):
			yield {
				'host': host,
			}

	def log_info(self, status, server_name_indication):
		super().log(f'{status:<6}  {server_name_indication}')

	def log_info_result(self, **kwargs):
		status = kwargs.get('status', '')
		if status:
			status = 'True'
			server_name_indication = kwargs.get('server_name_indication', '')
			self.log_info(status, server_name_indication)

	def init(self):
		super().init()
		self.log_info('Status', 'Server Name Indication')
		self.log_info('------', '----------------------')

	def task(self, payload):
		server_name_indication = payload['host']

		if not server_name_indication:
			return

		response = {
			'server_name_indication': server_name_indication,
		}

		try:
			socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			socket_client.settimeout(5)
			socket_client.connect((server_name_indication, 443))
			socket_client = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(
				socket_client, server_hostname=server_name_indication, do_handshake_on_connect=True
			)
			response['status'] = True
			self.task_success(server_name_indication)
			self.log_info_result(**response)

		except Exception:
			pass

		self.log_replace(server_name_indication)

	def complete(self):
		self.log_replace(self.colorize("Scan completed", "GREEN"))
		super().complete()
