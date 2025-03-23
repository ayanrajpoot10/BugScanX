import random
import requests
from bs4 import BeautifulSoup
from bugscanx.utils.http import USER_AGENTS, EXTRA_HEADERS
from .utils import RateLimiter

class DomainScraper:
    def __init__(self, rate_limit=1.0):
        self.headers = {
            "User-Agent": random.choice(USER_AGENTS),
            **EXTRA_HEADERS
        }
        self.rate_limiter = RateLimiter(rate_limit)
        self.session = requests.Session()
        self.session.timeout = 10.0

    def _make_request(self, url, method='get', data=None):
        self.rate_limiter.acquire()
        try:
            if method == 'get':
                response = self.session.get(url, headers=self.headers)
            else:
                response = self.session.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            return response
        except requests.RequestException:
            return None

    def fetch_domains(self, ip):
        raise NotImplementedError

    def close(self):
        self.session.close()

class RapidDNSScraper(DomainScraper):
    def fetch_domains(self, ip):
        response = self._make_request(f"https://rapiddns.io/sameip/{ip}")
        if not response:
            return []
        soup = BeautifulSoup(response.content, 'html.parser')
        return [row.find_all('td')[0].text.strip() 
                for row in soup.find_all('tr') if row.find_all('td')]

class YouGetSignalScraper(DomainScraper):
    def fetch_domains(self, ip):
        data = {'remoteAddress': ip, 'key': '', '_': ''}
        response = self._make_request("https://domains.yougetsignal.com/domains.php",
                                method='post', data=data)
        if not response:
            return []
        return [domain[0] for domain in response.json().get("domainArray", [])]

def get_scrapers():
    return [
        RapidDNSScraper(),
        YouGetSignalScraper()
    ]
