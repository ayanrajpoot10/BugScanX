import concurrent.futures
from rich import print
from bugscanx.utils import get_input, is_cidr

from .scrapers import get_scrapers
from .ip_utils import process_input, process_file
from .result_manager import ResultManager


def extract_domains(ip, scrapers):
    print(f"[cyan] Searching domains for IP: {ip}[/cyan]")
    domains = []
    for scraper in scrapers:
        domain_list = scraper.fetch_domains(ip)
        if domain_list:
            domains.extend(domain_list)
            
    domains = sorted(set(domains))
    return (ip, domains)


def process_ips(ips, output_file):
    if not ips:
        print("[bold red] No valid IPs/CIDRs to process.[/bold red]")
        return 0
        
    scrapers = get_scrapers()
    result_manager = ResultManager(output_file)
    
    total_ips = len(ips)
    processed = 0
    total_domains = 0
    
    def process_ip(ip):
        ip, domains = extract_domains(ip, scrapers)
        if domains:
            result_manager.save_result(ip, domains)
            nonlocal total_domains
            total_domains += len(domains)
            
        nonlocal processed
        processed += 1
        progress = processed / total_ips * 100
        print(f"[yellow] Progress: {processed}/{total_ips} IPs processed ({progress:.2f}%)[/yellow]")
        return ip, domains

    # Use ThreadPoolExecutor to parallelize requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_ip, ip): ip for ip in ips}
        for future in concurrent.futures.as_completed(futures):
            future.result()
    
    for scraper in scrapers:
        scraper.close()
        
    print(f"[green]\n All IPs processed! Total domains found: {total_domains}[/green]")
    return total_domains
    

def get_input_interactively():
    ips = []
    
    input_choice = get_input("Choose input type", "choice", 
                           choices=["Manual IP/CIDR", "IP/CIDR from file"])
    
    if input_choice == "Manual IP/CIDR":
        cidr = get_input("Enter an IP or CIDR", validators=[is_cidr])
        ips.extend(process_input(cidr))
    else:
        file_path = get_input("Enter the file path containing IPs/CIDRs", "file")
        ips.extend(process_file(file_path))
        
    output_file = get_input("Enter the output file path")
    return ips, output_file


def iplookup_main(ips=None, output_file=None):
    if ips is None or output_file is None:
        ips, output_file = get_input_interactively()
    process_ips(ips, output_file)

