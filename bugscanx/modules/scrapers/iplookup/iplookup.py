import concurrent.futures
from bugscanx.utils.common import get_input, is_cidr
from .sources import get_scrapers
from .utils import process_input, process_file
from .result_manager import ResultManager
from .logger import IPLookupConsole, console

def extract_domains(ip, scrapers, ip_console):
    ip_console.start_ip_scan(ip)
    domains = []
    for scraper in scrapers:
        domain_list = scraper.fetch_domains(ip)
        if domain_list:
            domains.extend(domain_list)
            
    domains = sorted(set(domains))
    return (ip, domains)

def process_ips(ips, output_file):
    if not ips:
        console.print("[bold red] No valid IPs/CIDRs to process.[/bold red]")
        return 0
        
    scrapers = get_scrapers()
    ip_console = IPLookupConsole()
    result_manager = ResultManager(output_file, ip_console)
    
    def process_ip(ip):
        ip, domains = extract_domains(ip, scrapers, ip_console)
        if domains:
            result_manager.save_result(ip, domains)
        return ip, domains

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_ip, ip): ip for ip in ips}
        for future in concurrent.futures.as_completed(futures):
            future.result()
    
    for scraper in scrapers:
        scraper.close()
        
    ip_console.print_final_summary(output_file)
    return ip_console.total_domains

def get_input_interactively():
    ips = []
    
    input_choice = get_input("Select input mode", "choice", 
                           choices=["Manual", "File"])
    
    if input_choice == "Manual":
        cidr = get_input("Enter IP or CIDR", validators=[is_cidr])
        ips.extend(process_input(cidr))
    else:
        file_path = get_input("Enter filename", "file")
        ips.extend(process_file(file_path))
        
    output_file = get_input("Enter output filename")
    return ips, output_file

def main(ips=None, output_file=None):
    if ips is None or output_file is None:
        ips, output_file = get_input_interactively()
    process_ips(ips, output_file)
