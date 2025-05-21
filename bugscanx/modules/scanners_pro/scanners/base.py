from ..concurrency.multithread import MultiThread


class BaseScanner(MultiThread):
    def convert_host_port(self, host, port):
        return host + (f':{port}' if port not in ['80', '443'] else '')

    def get_url(self, host, port):
        port = str(port)
        protocol = 'https' if port == '443' else 'http'
        return f'{protocol}://{self.convert_host_port(host, port)}'

    def filter_list(self, data):
        filtered_data = []
        for item in data:
            item = str(item).strip()
            if item.startswith(('#', '*')) or not item:
                continue
            filtered_data.append(item)
        return list(set(filtered_data))
