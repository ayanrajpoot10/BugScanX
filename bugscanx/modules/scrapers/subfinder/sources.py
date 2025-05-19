from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from .utils import RequestHandler

class SubdomainSource(RequestHandler, ABC):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.subdomains = set()

    @abstractmethod
    def fetch(self, domain):
        pass

class CrtshSource(SubdomainSource):
    def __init__(self):
        super().__init__("Crt.sh")

    def fetch(self, domain):
        response = self.get(f"https://crt.sh/?q=%25.{domain}&output=json")
        if response and response.headers.get('Content-Type') == 'application/json':
            for entry in response.json():
                self.subdomains.update(entry['name_value'].splitlines())
        return self.subdomains

class HackertargetSource(SubdomainSource):
    def __init__(self):
        super().__init__("Hackertarget")

    def fetch(self, domain):
        response = self.get(f"https://api.hackertarget.com/hostsearch/?q={domain}")
        if response and 'text' in response.headers.get('Content-Type', ''):
            self.subdomains.update(
                [line.split(",")[0] for line in response.text.splitlines()]
            )
        return self.subdomains

class RapidDnsSource(SubdomainSource):
    def __init__(self):
        super().__init__("RapidDNS")

    def fetch(self, domain):
        response = self.get(f"https://rapiddns.io/subdomain/{domain}?full=1")
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('td'):
                text = link.get_text(strip=True)
                if text.endswith(f".{domain}"):
                    self.subdomains.add(text)
        return self.subdomains

class AnubisDbSource(SubdomainSource):
    def __init__(self):
        super().__init__("AnubisDB")

    def fetch(self, domain):
        response = self.get(f"https://jldc.me/anubis/subdomains/{domain}")
        if response:
            self.subdomains.update(response.json())
        return self.subdomains

class AlienVaultSource(SubdomainSource):
    def __init__(self):
        super().__init__("AlienVault")

    def fetch(self, domain):
        response = self.get(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns")
        if response:
            for entry in response.json().get("passive_dns", []):
                hostname = entry.get("hostname")
                if hostname:
                    self.subdomains.add(hostname)
        return self.subdomains

class CertSpotterSource(SubdomainSource):
    def __init__(self):
        super().__init__("CertSpotter")

    def fetch(self, domain):
        response = self.get(f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names")
        if response:
            for cert in response.json():
                self.subdomains.update(cert.get('dns_names', []))
        return self.subdomains

def get_sources():
    return [
        CrtshSource(),
        HackertargetSource(),
        RapidDnsSource(),
        AnubisDbSource(),
        AlienVaultSource(),
        CertSpotterSource(),
    ]
