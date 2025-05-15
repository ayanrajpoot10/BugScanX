import os
import requests
import threading
from rich import print
from concurrent.futures import ThreadPoolExecutor, as_completed
from bugscanx.utils.common import get_input
from .logger import SubFinderConsole
from .sources import get_all_sources, get_bulk_sources
from .utils import is_valid_domain, filter_valid_subdomains

class SubFinder:
    def __init__(self):
        self.console = SubFinderConsole()
    
    def process_domain(self, domain, output_file, sources, total, completed_counter):
        if not is_valid_domain(domain):
            with completed_counter.get_lock():
                completed_counter.value += 1
            return set()

        self.console.start_domain_scan(domain)
        self.console.show_progress(completed_counter.value, total)
        
        with requests.Session() as session:
            results = []
            with ThreadPoolExecutor(max_workers=6) as executor:
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

        self.console.update_domain_stats(domain, len(subdomains))
        self.console.print_domain_complete(domain, len(subdomains))

        if subdomains:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("\n".join(sorted(subdomains)) + "\n")

        with completed_counter.get_lock():
            completed_counter.value += 1
            self.console.show_progress(completed_counter.value, total)

        return subdomains

    def run(self, domains, output_file, sources):
        if not domains:
            self.console.print_error("No valid domains provided")
            return

        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        completed_counter = threading.Value('i', 0)
        all_subdomains = set()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_domain = {
                executor.submit(
                    self.process_domain, 
                    domain, 
                    output_file, 
                    sources, 
                    len(domains), 
                    completed_counter
                ): domain for domain in domains
            }
            
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    if result:
                        all_subdomains.update(result)
                except Exception as e:
                    self.console.print(f"Error processing {domain}: {str(e)}")

        self.console.print_final_summary(output_file)
        return all_subdomains

def main():
    domains = []
    input_type = get_input("Select input mode", "choice", 
                        choices=["Manual", "File"])
    
    if input_type == "Manual":
        domain_input = get_input("Enter domain(s)")
        domains = [d.strip() for d in domain_input.split(',') if is_valid_domain(d.strip())]
        sources = get_all_sources()
        default_output = f"{domains[0]}_subdomains.txt"

    else:
        file_path = get_input("Enter filename", "file")
        with open(file_path, 'r') as f:
            domains = [d.strip() for d in f if is_valid_domain(d.strip())]
        sources = get_bulk_sources()
        default_output = f"{file_path.rsplit('.', 1)[0]}_subdomains.txt"

    if not domains:
        print("[bold red] No valid domains provided")
        return

    output_file = get_input("Enter output filename", default=default_output)
    subfinder = SubFinder()
    subfinder.run(domains, output_file, sources)
