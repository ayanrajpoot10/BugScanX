from bs4 import BeautifulSoup

from .utils import make_request

class SubdomainSource:
    def __init__(self, name):
        self.name = name
        self.subdomains = set()
    
    def fetch(self, domain, session=None):
        raise NotImplementedError

class CrtshSource(SubdomainSource):
    def __init__(self):
        super().__init__("Crt.sh")
    
    def fetch(self, domain, session=None):
        response = make_request(f"https://crt.sh/?q=%25.{domain}&output=json", session)
        if response and response.headers.get('Content-Type') == 'application/json':
            for entry in response.json():
                self.subdomains.update(entry['name_value'].splitlines())
        return self.subdomains

class HackertargetSource(SubdomainSource):
    def __init__(self):
        super().__init__("Hackertarget")
    
    def fetch(self, domain, session=None):
        response = make_request(f"https://api.hackertarget.com/hostsearch/?q={domain}", session)
        if response and 'text' in response.headers.get('Content-Type', ''):
            self.subdomains.update([line.split(",")[0] for line in response.text.splitlines()])
        return self.subdomains

class RapidDnsSource(SubdomainSource):
    def __init__(self):
        super().__init__("RapidDNS")
    
    def fetch(self, domain, session=None):
        response = make_request(f"https://rapiddns.io/subdomain/{domain}?full=1", session)
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
    
    def fetch(self, domain, session=None):
        response = make_request(f"https://jldc.me/anubis/subdomains/{domain}", session)
        if response:
            self.subdomains.update(response.json())
        return self.subdomains

class AlienVaultSource(SubdomainSource):
    def __init__(self):
        super().__init__("AlienVault")
    
    def fetch(self, domain, session=None):
        response = make_request(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns", session)
        if response:
            for entry in response.json().get("passive_dns", []):
                hostname = entry.get("hostname")
                if hostname:
                    self.subdomains.add(hostname)
        return self.subdomains

class CertSpotterSource(SubdomainSource):
    def __init__(self):
        super().__init__("CertSpotter")
    
    def fetch(self, domain, session=None):
        response = make_request(f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names", session)
        if response:
            for cert in response.json():
                self.subdomains.update(cert.get('dns_names', []))
        return self.subdomains

def get_all_sources():
    return [
        CrtshSource(),
        HackertargetSource(),
        RapidDnsSource(),
        AnubisDbSource(),
        AlienVaultSource(),
        CertSpotterSource(),
    ]

def get_bulk_sources():
    return [
        CrtshSource(),
        HackertargetSource(),
        RapidDnsSource(),
        AnubisDbSource(),
        AlienVaultSource(),
        CertSpotterSource(),
    ]
