import random
import httpx
from bs4 import BeautifulSoup
from bugscanx.utils import USER_AGENTS, EXTRA_HEADERS
from .rate_limiter import RateLimiter

class DomainScraper:
    def __init__(self, rate_limit=1.0):
        self.headers = {
            "User-Agent": random.choice(USER_AGENTS),
            **EXTRA_HEADERS
        }
        self.rate_limiter = RateLimiter(rate_limit)
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)

    async def _make_request(self, url, method='get', data=None):
        await self.rate_limiter.acquire()
        try:
            if method == 'get':
                response = await self.client.get(url, headers=self.headers)
            else:
                response = await self.client.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            return response
        except httpx.HTTPError:
            return None

    async def fetch_domains(self, ip):
        """Method to be implemented by subclasses"""
        raise NotImplementedError

    async def close(self):
        await self.client.aclose()


class RapidDNSScraper(DomainScraper):
    async def fetch_domains(self, ip):
        response = await self._make_request(f"https://rapiddns.io/sameip/{ip}")
        if not response:
            return []
        soup = BeautifulSoup(response.content, 'html.parser')
        return [row.find_all('td')[0].text.strip() 
                for row in soup.find_all('tr') if row.find_all('td')]


class YouGetSignalScraper(DomainScraper):
    async def fetch_domains(self, ip):
        data = {'remoteAddress': ip, 'key': '', '_': ''}
        response = await self._make_request("https://domains.yougetsignal.com/domains.php",
                                    method='post', data=data)
        if not response:
            return []
        return [domain[0] for domain in response.json().get("domainArray", [])]


# Factory function to get all available scrapers
def get_scrapers():
    return [
        RapidDNSScraper(),
        YouGetSignalScraper()
    ]
