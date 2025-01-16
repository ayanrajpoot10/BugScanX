import re
import random
import requests
from bugscanx.modules import *
from bs4 import BeautifulSoup
from rich.console import Console
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
session = requests.Session()
console = Console()

def get_random_headers():
    headers = HEADERS.copy()
    headers["user-agent"] = random.choice(USER_AGENTS)
    return headers

def make_request(url):
    try:
        response = session.get(url, headers=get_random_headers(), timeout=SUBFINDER_TIMEOUT)
        if response.status_code == 200:
            return response
    except requests.RequestException:
        pass
    return None

def is_valid_domain(domain):
    regex = re.compile(
        r'^(?:[a-zA-Z0-9]'
        r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
        r'[a-zA-Z]{2,6}$'
    )
    return re.match(regex, domain) is not None

def fetch_subdomains(source_func, domain):
    try:
        subdomains = source_func(domain)
        return set(sub for sub in subdomains if isinstance(sub, str))
    except Exception:
        return set()

def crtsh_subdomains(domain):
    subdomains = set()
    response = make_request(f"https://crt.sh/?q=%25.{domain}&output=json")
    if response and response.headers.get('Content-Type') == 'application/json':
        for entry in response.json():
            subdomains.update(entry['name_value'].splitlines())
    return subdomains

def hackertarget_subdomains(domain):
    subdomains = set()
    response = make_request(f"https://api.hackertarget.com/hostsearch/?q={domain}")
    if response and 'text' in response.headers.get('Content-Type', ''):
        subdomains.update([line.split(",")[0] for line in response.text.splitlines()])
    return subdomains

def rapiddns_subdomains(domain):
    subdomains = set()
    response = make_request(f"https://rapiddns.io/subdomain/{domain}?full=1")
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('td'):
            text = link.get_text(strip=True)
            if text.endswith(f".{domain}"):
                subdomains.add(text)
    return subdomains

def anubisdb_subdomains(domain):
    subdomains = set()
    response = make_request(f"https://jldc.me/anubis/subdomains/{domain}")
    if response:
        subdomains.update(response.json())
    return subdomains

def alienvault_subdomains(domain):
    subdomains = set()
    response = make_request(f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns")
    if response:
        for entry in response.json().get("passive_dns", []):
            subdomains.add(entry.get("hostname"))
    return subdomains

def urlscan_subdomains(domain):
    subdomains = set()
    response = make_request(f"https://urlscan.io/api/v1/search/?q=domain:{domain}")
    if response:
        data = response.json()
        for result in data.get('results', []):
            page_url = result.get('page', {}).get('domain')
            if page_url and page_url.endswith(f".{domain}"):
                subdomains.add(page_url)
    return subdomains

recently_seen_subdomains = set()

def c99_subdomains(domain, days=10):
    base_url = "https://subdomainfinder.c99.nl/scans"
    subdomains = set()
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    urls = [f"{base_url}/{date}/{domain}" for date in dates]

    def fetch_url(url):
        response = make_request(url)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                text = link.get_text(strip=True)
                if text.endswith(f".{domain}") and text not in recently_seen_subdomains:
                    subdomains.add(text)
                    recently_seen_subdomains.add(text)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_url, url) for url in urls]
        for future in as_completed(futures):
            future.result()

    return subdomains

def process_domain(domain, output_file, sources):
    if not is_valid_domain(domain):
        console.print(f"\n Invalid domain: {domain}", style="bold red")
        return

    console.print(f" Enumerating {domain}\n", style="bold cyan")
    
    subdomains = set()

    with ThreadPoolExecutor(max_workers=min(len(sources), 10)) as executor:
        futures = {executor.submit(fetch_subdomains, source, domain): source for source in sources}
        for future in as_completed(futures):
            subdomains.update(future.result())

    console.print(f"\n Completed {domain} - {len(subdomains)} subdomains found", style="bold green")
    
    with open(output_file, "a", encoding="utf-8") as file:
        file.write(f"\n# Subdomains for {domain}\n")
        for subdomain in sorted(subdomains):
            if is_valid_domain(subdomain):
                file.write(f"{subdomain}\n")

def find_subdomains():
    input_choice = get_input("\n Enter 1 for single domain or 2 for txt file", validator=choice_validator)
    
    if input_choice == '1':
        domain = get_input(prompt=" Enter the domain to find subdomains", validator=not_empty_validator)
        if not is_valid_domain(domain):
            console.print(f"\n Invalid domain: {domain}", style="bold red")
            return
        domains_to_process = [domain]
        sources = [
            crtsh_subdomains, hackertarget_subdomains, rapiddns_subdomains,
            anubisdb_subdomains, alienvault_subdomains,
            urlscan_subdomains, c99_subdomains
        ]
        default_output_file = f"{domain}_subdomains.txt"
        
    elif input_choice == '2':
        file_path = get_input(prompt=" Enter the path to the file containing domains", validator=file_path_validator, completer=completer)
        with open(file_path, 'r') as file:
            domains_to_process = [line.strip() for line in file if line.strip() and is_valid_domain(line.strip())]

        sources = [
            crtsh_subdomains, hackertarget_subdomains, rapiddns_subdomains,
            anubisdb_subdomains, alienvault_subdomains,
            urlscan_subdomains
        ]
        default_output_file = f"{file_path.rsplit('.', 1)[0]}_subdomains.txt"

    output_file = get_input(prompt=" Enter the output file name", default=default_output_file, validator=not_empty_validator)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_domain, domain, output_file, sources): domain for domain in domains_to_process}
        for future in as_completed(futures):
            future.result()

    console.print(f" All results saved to {output_file}", style="bold green")
