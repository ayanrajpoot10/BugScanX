import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from bugscanx.utils import get_input
from .subfinder_console import SubFinderConsole
from .subfinder_sources import get_all_sources, get_bulk_sources
from .subfinder_utils import is_valid_domain, filter_valid_subdomains
from .concurrent_processor import ConcurrentProcessor

def process_domain(domain, output_file, sources, console, total=1, current=1):
    if not is_valid_domain(domain):
        return set()

    console.start_domain_scan(domain)
    console.show_progress(current, total)
    
    with requests.Session() as session:
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(source.fetch, domain, session): source.name
                for source in sources
            }
            
            for future in as_completed(future_to_source):
                try:
                    found = future.result()
                    filtered = filter_valid_subdomains(found, domain)
                    results.append(filtered)
                except Exception:
                    results.append(set())
        
        subdomains = set().union(*results) if results else set()

    console.update_domain_stats(domain, len(subdomains))
    console.print_domain_complete(domain, len(subdomains))

    if subdomains:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write("\n".join(sorted(subdomains)) + "\n")

    return subdomains

def find_subdomains():
    console = SubFinderConsole()
    domains = []
    
    if get_input("Select input type", "choice", 
               choices=["single domain", "bulk domains from file"]) == "single domain":
        domains = [get_input("Enter the domain to find subdomains")]
        sources = get_all_sources()
        output_file = f"{domains[0]}_subdomains.txt"
    else:
        file_path = get_input("Enter the path to the file containing domains", "file")
        with open(file_path, 'r') as f:
            domains = [d.strip() for d in f if is_valid_domain(d.strip())]
        sources = get_bulk_sources()
        output_file = f"{file_path.rsplit('.', 1)[0]}_subdomains.txt"

    if not domains:
        console.print_error("No valid domains provided")
        return

    output_file = get_input("Enter the output file name", default=output_file)
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    
    processor = ConcurrentProcessor(max_workers=3)
    
    def process_domain_wrapper(domain, index):
        try:
            return process_domain(domain, output_file, sources, console, len(domains), index + 1)
        except Exception:
            return set()
    
    processor.process_items(
        domains,
        process_domain_wrapper,
        on_error=lambda domain, error: None
    )

    console.print_final_summary(output_file)
