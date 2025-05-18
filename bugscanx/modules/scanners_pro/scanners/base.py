from ..concurrency.multithread import MultiThread
from ..concurrency.logger import Logger


class BaseScanner(MultiThread):

    @classmethod
    def colorize(cls, text, color):
        return Logger.colorize(text, color)

    def convert_host_port(self, host, port):
        return host + (f':{port}' if port not in ['80', '443'] else '')

    def get_url(self, host, port, uri=None):
        port = str(port)
        protocol = 'https' if port == '443' else 'http'
        base_url = f'{protocol}://{self.convert_host_port(host, port)}'
        return f'{base_url}/{uri}' if uri else base_url

    def filter_list(self, data):
        filtered_data = []
        for item in data:
            item = str(item).strip()
            if item.startswith(('#', '*')) or not item:
                continue
            filtered_data.append(item)
        return list(set(filtered_data))

    def hide_cursor(self):
        print('\033[?25l', end='', flush=True)

    def show_cursor(self):
        print('\033[?25h', end='', flush=True)

    def init(self):
        self._threads = self.threads or self._threads
        self.hide_cursor()
        print()

    def complete(self):
        self.show_cursor()
        print()
