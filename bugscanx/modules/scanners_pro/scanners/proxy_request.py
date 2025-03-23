import requests
from urllib.parse import urlparse, urlunparse
from .direct import DirectScanner

class Proxy2Scanner(DirectScanner):
    def __init__(self, proxy=None, auth=None):
        super().__init__()
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

    def request(self, method, url, **kwargs):
        method = method.upper()
        kwargs['timeout'] = self.DEFAULT_TIMEOUT
        max_attempts = self.DEFAULT_RETRY
        
        for attempt in range(max_attempts):
            self.log_replace(f"{method} (via proxy) {url}")
            try:
                return self.session.request(method, url, **kwargs)
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.Timeout,
                    requests.exceptions.ProxyError) as e:
                wait_time = 1 if isinstance(e, requests.exceptions.ConnectionError) else 5
                for _ in self.sleep(wait_time):
                    self.log_replace(f"{method} (via proxy) {url}")
                if attempt == max_attempts - 1:
                    return None
        return None
