import requests

from .multithread import MultiThread


class MultiThreadRequest(MultiThread):
	requests = requests

	def request_connection_error(self, method, url, **_):
		for _ in self.sleep(1):
			self.log_replace(method, url, 'connection error')
		return 1

	def request_read_timeout(self, method, url, **_):
		for remains in self.sleep(10):
			self.log_replace(method, url, 'read timeout', remains)
		return 1

	def request_timeout(self, method, url, **_):
		for remains in self.sleep(5):
			self.log_replace(method, url, 'timeout', remains)
		return 1

	def request(self, method, url, **kwargs):
		method = method.upper()

		kwargs['timeout'] = kwargs.get('timeout', 5)

		retry = int(kwargs.pop('retry', 5))

		while retry > 0:
			self.log_replace(method, url)

			try:
				return self.requests.request(method, url, **kwargs)

			except requests.exceptions.ConnectionError:
				retry_decrease = self.request_connection_error(method, url, **kwargs)
				retry -= retry_decrease or 0

			except requests.exceptions.ReadTimeout:
				retry_decrease = self.request_read_timeout(method, url, **kwargs)
				retry -= retry_decrease or 0

			except requests.exceptions.Timeout:
				retry_decrease = self.request_timeout(method, url, **kwargs)
				retry -= retry_decrease or 0

		return None
