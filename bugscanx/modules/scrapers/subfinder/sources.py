from abc import ABC, abstractmethod
import datetime
from bs4 import BeautifulSoup
from .utils import RequestHandler


class SubdomainSource(RequestHandler, ABC):
    def __init__(self, name):
        super().__init__()
        self.name = name

    @abstractmethod
    def fetch(self, domain):
        pass


class CrtshSource(SubdomainSource):
    def __init__(self):
        super().__init__("Crt.sh")

    def fetch(self, domain):
        subdomains = set()
        response = self.get(f"https://crt.sh/?q=%25.{domain}&output=json")
        if response and response.headers.get('Content-Type') == 'application/json':
            for entry in response.json():
                subdomains.update(entry['name_value'].splitlines())
        return subdomains


class HackertargetSource(SubdomainSource):
    def __init__(self):
        super().__init__("Hackertarget")

    def fetch(self, domain):
        subdomains = set()
        response = self.get(f"https://api.hackertarget.com/hostsearch/?q={domain}")
        if response and 'text' in response.headers.get('Content-Type', ''):
            subdomains.update(
                [line.split(",")[0] for line in response.text.splitlines()]
            )
        return subdomains


class RapidDnsSource(SubdomainSource):
    def __init__(self):
        super().__init__("RapidDNS")

    def fetch(self, domain):
        subdomains = set()
        response = self.get(f"https://rapiddns.io/subdomain/{domain}?full=1")
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('td'):
                text = link.get_text(strip=True)
                if text.endswith(f".{domain}"):
                    subdomains.add(text)
        return subdomains


class AnubisDbSource(SubdomainSource):
    def __init__(self):
        super().__init__("AnubisDB")

    def fetch(self, domain):
        subdomains = set()
        response = self.get(f"https://jldc.me/anubis/subdomains/{domain}")
        if response:
            subdomains.update(response.json())
        return subdomains


class AlienVaultSource(SubdomainSource):
    def __init__(self):
        super().__init__("AlienVault")

    def fetch(self, domain):
        subdomains = set()
        response = self.get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns")
        if response:
            for entry in response.json().get("passive_dns", []):
                hostname = entry.get("hostname")
                if hostname:
                    subdomains.add(hostname)
        return subdomains


class CertSpotterSource(SubdomainSource):
    def __init__(self):
        super().__init__("CertSpotter")

    def fetch(self, domain):
        subdomains = set()
        response = self.get(f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names")
        if response:
            for cert in response.json():
                subdomains.update(cert.get('dns_names', []))
        return subdomains


class C99Source(SubdomainSource):
    def __init__(self):
        super().__init__("C99")

    def fetch(self, domain):
        subdomains = set()
        dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d') 
                for i in range(7)]
        
        for date in dates:
            url = f"https://subdomainfinder.c99.nl/scans/{date}/{domain}"
            response = self.get(url)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.select('td a.link.sd'):
                    text = link.get_text(strip=True)
                    if text.endswith(f".{domain}"):
                        subdomains.add(text)
                if subdomains:
                    break
        return subdomains


def get_sources():
    return [
        CrtshSource(),
        HackertargetSource(),
        RapidDnsSource(),
        AnubisDbSource(),
        AlienVaultSource(),
        CertSpotterSource(),
        # C99Source() 
    ]
