from abc import ABC, abstractmethod
import math
from bs4 import BeautifulSoup
from .utils import RequestHandler


class DomainSource(RequestHandler, ABC):
    def __init__(self, name):
        super().__init__()
        self.name = name

    @abstractmethod
    def fetch(self, ip):
        pass


class RapidDNSSource(DomainSource):
    def __init__(self):
        super().__init__("RapidDNS")

    def _extract_domains_from_page(self, soup):
        return {
            row.find_all('td')[0].text.strip()
            for row in soup.find_all('tr')
            if row.find_all('td')
        }

    def _get_total_results(self, soup):
        span = soup.find("span", style="color: #39cfca; ")
        if span and span.text.strip().isdigit():
            return int(span.text.strip())
        return 0

    def fetch(self, ip):
        domains = set()
        response = self.get(f"https://rapiddns.io/sameip/{ip}")
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            domains.update(self._extract_domains_from_page(soup))
            
            total_results = self._get_total_results(soup)
            if total_results > 100:
                total_pages = math.ceil(total_results / 100)
                
                for page in range(2, total_pages + 1):
                    response = self.get(f"https://rapiddns.io/sameip/{ip}?page={page}")
                    if response:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        domains.update(self._extract_domains_from_page(soup))
        return domains


class YouGetSignalSource(DomainSource):
    def __init__(self):
        super().__init__("YouGetSignal")

    def fetch(self, ip):
        domains = set()
        data = {'remoteAddress': ip, 'key': '', '_': ''}
        response = self.post("https://domains.yougetsignal.com/domains.php", data=data)
        if response:
            domains.update(
                domain[0] for domain in response.json().get("domainArray", [])
            )
        return domains


def get_scrapers():
    return [
        RapidDNSSource(),
        YouGetSignalSource()
    ]
