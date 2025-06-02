import requests
from urllib.parse import urlparse, urlunparse
from .direct import DirectScannerBase


class Proxy2ScannerBase(DirectScannerBase):
    def __init__(
        self,
        proxy=None,
        auth=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.proxy = proxy or {}
        self.auth = auth
        self.session = requests.Session()
        if self.proxy:
            self.session.proxies.update(self.proxy)
        if self.auth:
            self.session.auth = self.auth
        self.requests = self.session

    def set_proxy(self, proxy, username=None, password=None):
        if not proxy.startswith(('http://', 'https://')):
            proxy = f'http://{proxy}'

        parsed = urlparse(proxy)
        proxy_url = urlunparse(parsed)

        self.proxy = {
            'http': proxy_url,
            'https': proxy_url
        }
        self.session.proxies.update(self.proxy)

        if username and password:
            from requests.auth import HTTPProxyAuth
            self.auth = HTTPProxyAuth(username, password)
            self.session.auth = self.auth

        return self

    def request(self, method, url, **kwargs):
        method = method.upper()
        kwargs['timeout'] = self.DEFAULT_TIMEOUT
        max_attempts = self.DEFAULT_RETRY

        for attempt in range(max_attempts):
            self.log_progress(f"{method} (via proxy) {url}")
            try:
                return self.session.request(method, url, **kwargs)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.ProxyError
            ) as e:
                wait_time = 1 if isinstance(e, requests.exceptions.ConnectionError) else 5
                for _ in self.sleep(wait_time):
                    self.log_progress(f"{method} (via proxy) {url}")
                if attempt == max_attempts - 1:
                    return None
        return None


class HostProxy2Scanner(Proxy2ScannerBase):
    def __init__(
        self,
        method_list=None,
        input_file=None,
        port_list=None,
        no302=False,
        threads=50,
        **kwargs
    ):
        super().__init__(
            method_list=method_list,
            port_list=port_list,
            no302=no302,
            threads=threads,
            is_cidr_input=False,
            **kwargs
        )
        self.input_file = input_file

        if self.input_file:
            self.set_host_total(self.input_file)

    def log_info(self, **kwargs):
        server = kwargs.get('server', '')
        kwargs['server'] = ((server[:12] + "...") if len(server) > 12 
                          else f"{server:<12}")

        messages = [
            self.logger.colorize(f"{{method:<6}}", "CYAN"),
            self.logger.colorize(f"{{status_code:<4}}", "GREEN"),
            self.logger.colorize(f"{{server:<15}}", "MAGENTA"),
            self.logger.colorize(f"{{port:<4}}", "ORANGE"),
            self.logger.colorize(f"{{ip:<16}}", "BLUE"),
            self.logger.colorize(f"{{host}}", "LGRAY")
        ]

        self.logger.log('  '.join(messages).format(**kwargs))

    def generate_tasks(self):
        for method in self.method_list:
            for host in self.generate_hosts_from_file(self.input_file):
                for port in self.port_list:
                    yield {
                        'method': method.upper(),
                        'host': host,
                        'port': port,
                    }

    def init(self):
        self.log_info(method='Method', status_code='Code', server='Server', port='Port', ip='IP', host='Host')
        self.log_info(method='------', status_code='----', server='------', port='----', ip='--', host='----')

    def _handle_success(self, data):
        self.success(data)
        self.log_info(**data)


class CIDRProxy2Scanner(Proxy2ScannerBase):
    def __init__(
        self,
        method_list=None,
        cidr_ranges=None,
        port_list=None,
        no302=False,
        threads=50,
        **kwargs
    ):
        super().__init__(
            method_list=method_list,
            port_list=port_list,
            no302=no302,
            threads=threads,
            is_cidr_input=True,
            cidr_ranges=cidr_ranges,
            **kwargs
        )
        self.cidr_ranges = cidr_ranges or []
        
        if self.cidr_ranges:
            self.set_cidr_total(self.cidr_ranges)

    def log_info(self, **kwargs):
        server = kwargs.get('server', '')
        kwargs['server'] = ((server[:12] + "...") if len(server) > 12 
                          else f"{server:<12}")

        messages = [
            self.logger.colorize(f"{{method:<6}}", "CYAN"),
            self.logger.colorize(f"{{status_code:<4}}", "GREEN"),
            self.logger.colorize(f"{{server:<15}}", "MAGENTA"),
            self.logger.colorize(f"{{port:<4}}", "ORANGE"),
            self.logger.colorize(f"{{host}}", "LGRAY")
        ]

        self.logger.log('  '.join(messages).format(**kwargs))

    def generate_tasks(self):
        for method in self.method_list:
            for host in self.generate_cidr_hosts(self.cidr_ranges):
                for port in self.port_list:
                    yield {
                        'method': method.upper(),
                        'host': host,
                        'port': port,
                    }

    def init(self):
        self.log_info(method='Method', status_code='Code', server='Server', port='Port', host='Host')
        self.log_info(method='------', status_code='----', server='------', port='----', host='----')

    def _handle_success(self, data):
        self.success(data)
        self.log_info(**data)
