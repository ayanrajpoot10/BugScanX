from .threading.multithread_requests import MultiThreadRequest

class BugScanner(MultiThreadRequest):
	threads: int

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