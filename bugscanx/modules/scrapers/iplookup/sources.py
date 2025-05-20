from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from .utils import RequestHandler


class DomainSource(RequestHandler, ABC):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.domains = set()

    @abstractmethod
    def fetch(self, ip):
        pass


class RapidDNSSource(DomainSource):
    def __init__(self):
        super().__init__("RapidDNS")

    def fetch(self, ip):
        response = self.get(f"https://rapiddns.io/sameip/{ip}")
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            self.domains.update(
                row.find_all('td')[0].text.strip()
                for row in soup.find_all('tr')
                if row.find_all('td')
            )
        return self.domains


class YouGetSignalSource(DomainSource):
    def __init__(self):
        super().__init__("YouGetSignal")

    def fetch(self, ip):
        data = {'remoteAddress': ip, 'key': '', '_': ''}
        response = self.post("https://domains.yougetsignal.com/domains.php", data=data)
        if response:
            self.domains.update(
                domain[0] for domain in response.json().get("domainArray", [])
            )
        return self.domains


def get_scrapers():
    return [
        RapidDNSSource(),
        YouGetSignalSource()
    ]
