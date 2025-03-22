import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from .subfinder_console import SubFinderConsole
from .subfinder_utils import is_valid_domain, filter_valid_subdomains

class SubdomainFinder:
    def __init__(self, console=None):
        self.console = console or SubFinderConsole()
    
    def process_domain(self, domain, output_file, sources, total, completed_counter):
        if not is_valid_domain(domain):
            with completed_counter.get_lock():
                completed_counter.value += 1
            return set()

        self.console.start_domain_scan(domain)
        self.console.show_progress(completed_counter.value, total)
        
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

        self.console.update_domain_stats(domain, len(subdomains))
        self.console.print_domain_complete(domain, len(subdomains))

        if subdomains:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("\n".join(sorted(subdomains)) + "\n")

        with completed_counter.get_lock():
            completed_counter.value += 1
            self.console.show_progress(completed_counter.value, total)

        return subdomains

    def find_subdomains(self, domains, output_file, sources):
        if not domains:
            self.console.print_error("No domains provided")
            return

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
