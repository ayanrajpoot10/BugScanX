import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from bugscanx.utils.common import get_input
from .logger import SubFinderConsole
from .sources import get_sources
from .utils import DomainValidator, CursorManager


class SubFinder:
    def __init__(self):
        self.console = SubFinderConsole()
        self.completed = 0
        self.cursor_manager = CursorManager()

    def _fetch_from_source(self, source, domain):
        try:
            found = source.fetch(domain)
            return DomainValidator.filter_valid_subdomains(found, domain)
        except Exception:
            return set()

    @staticmethod
    def save_subdomains(subdomains, output_file):
        if subdomains:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("\n".join(sorted(subdomains)) + "\n")

    def process_domain(self, domain, output_file, sources, total):
        if not DomainValidator.is_valid_domain(domain):
            self.completed += 1
            return set()

        self.console.print_domain_start(domain)
        self.console.print_progress(self.completed, total)
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(self._fetch_from_source, source, domain)
                for source in sources
            ]
            results = [f.result() for f in as_completed(futures)]

        subdomains = set().union(*results) if results else set()

        self.console.update_domain_stats(domain, len(subdomains))
        self.console.print_domain_complete(domain, len(subdomains))
        self.save_subdomains(subdomains, output_file)

        self.completed += 1
        self.console.print_progress(self.completed, total)
        return subdomains

    def run(self, domains, output_file, sources):
        if not domains:
            self.console.print_error("No valid domains provided")
            return

        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        self.completed = 0
        all_subdomains = set()
        total = len(domains)

        with self.cursor_manager:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(self.process_domain, domain, output_file, sources, total)
                    for domain in domains
                ]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        all_subdomains.update(result)
                    except Exception as e:
                        self.console.print(f"Error processing domain: {str(e)}")

            self.console.print_final_summary(output_file)
            return all_subdomains


def main():
    scanner_choice = get_input("Select Enumeration Mode", "choice",
                              choices=["SubFinder (passive)", "SubBrute (active)"])
    
    if scanner_choice == "SubBrute (active)":
        from .subbrute.subbrute import main as subbrute_main
        subbrute_main()
    
    else:
        domains = []
        sources = get_sources()
        input_type = get_input("Select input mode", "choice",
                               choices=["Manual", "File"])

        if input_type == "Manual":
            domain_input = get_input("Enter domain(s)")
            domains = [d.strip() for d in domain_input.split(',') if DomainValidator.is_valid_domain(d.strip())]
            default_output = f"{domains[0]}_subdomains.txt" if domains else "subdomains.txt"
        else:
            file_path = get_input("Enter filename", "file")
            with open(file_path, 'r') as f:
                domains = [d.strip() for d in f if DomainValidator.is_valid_domain(d.strip())]
            default_output = f"{file_path.rsplit('.', 1)[0]}_subdomains.txt"

        output_file = get_input("Enter output filename", default=default_output)
        subfinder = SubFinder()
        subfinder.run(domains, output_file, sources)
