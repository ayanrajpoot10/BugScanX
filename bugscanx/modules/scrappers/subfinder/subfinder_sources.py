import asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from bugscanx.modules.scrappers.subfinder.subfinder_utils import make_request

class SubdomainSource:
    def __init__(self, name):
        self.name = name
        self.subdomains = set()
    
    async def fetch(self, domain, client):
        raise NotImplementedError

class CrtshSource(SubdomainSource):
    def __init__(self):
        super().__init__("Crt.sh")
    
    async def fetch(self, domain, client):
        response = await make_request(f"https://crt.sh/?q=%25.{domain}&output=json", client)
        if response and response.headers.get('Content-Type') == 'application/json':
            for entry in response.json():
                self.subdomains.update(entry['name_value'].splitlines())
        return self.subdomains

class HackertargetSource(SubdomainSource):
    def __init__(self):
        super().__init__("Hackertarget")
    
    async def fetch(self, domain, client):
        response = await make_request(f"https://api.hackertarget.com/hostsearch/?q={domain}", client)
        if response and 'text' in response.headers.get('Content-Type', ''):
            self.subdomains.update([line.split(",")[0] for line in response.text.splitlines()])
        return self.subdomains

class RapidDnsSource(SubdomainSource):
    def __init__(self):
        super().__init__("RapidDNS")
    
    async def fetch(self, domain, client):
        response = await make_request(f"https://rapiddns.io/subdomain/{domain}?full=1", client)
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
    
    async def fetch(self, domain, client):
        response = await make_request(f"https://jldc.me/anubis/subdomains/{domain}", client)
        if response:
            self.subdomains.update(response.json())
        return self.subdomains

class AlienVaultSource(SubdomainSource):
    def __init__(self):
        super().__init__("AlienVault")
    
    async def fetch(self, domain, client):
        response = await make_request(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns", client)
        if response:
            for entry in response.json().get("passive_dns", []):
                hostname = entry.get("hostname")
                if hostname:
                    self.subdomains.add(hostname)
        return self.subdomains

class C99Source(SubdomainSource):
    def __init__(self):
        super().__init__("C99")
        self.recently_seen_subdomains = set()
    
    async def fetch(self, domain, client, days=10):
        base_url = "https://subdomainfinder.c99.nl/scans"
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        urls = [f"{base_url}/{date}/{domain}" for date in dates]

        async def fetch_url(url):
            response = await make_request(url, client)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                new_subdomains = {link.get_text(strip=True) for link in soup.select('td a.link.sd')}
                self.subdomains.update(new_subdomains - self.recently_seen_subdomains)
                self.recently_seen_subdomains.update(new_subdomains)

        await asyncio.gather(*[fetch_url(url) for url in urls])
        return self.subdomains

def get_all_sources():
    return [
        CrtshSource(),
        HackertargetSource(),
        RapidDnsSource(),
        AnubisDbSource(),
        AlienVaultSource(),
        C99Source()
    ]

def get_bulk_sources():
    return [
        CrtshSource(),
        HackertargetSource(),
        RapidDnsSource(),
        AnubisDbSource(),
        AlienVaultSource(),
    ]
