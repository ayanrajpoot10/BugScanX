import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from bugscanx.utils.common import get_input, get_confirm
from .logger import SubBruteConsole
from .utils import DomainValidator, SubdomainBruteforcer, CursorManager


class SubBrute:
    def __init__(self, wordlist_path=None, max_workers=50, dns_timeout=3, enable_wildcard_filtering=True):
        self.console = SubBruteConsole()
        self.completed = 0
        self.cursor_manager = CursorManager()
        
        if wordlist_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            wordlist_path = os.path.join(current_dir, 'wordlist_example.txt')
            
        self.bruteforcer = SubdomainBruteforcer(
            wordlist_path=wordlist_path,
            max_workers=max_workers,
            timeout=dns_timeout,
            enable_wildcard_filtering=enable_wildcard_filtering
        )

    def _create_progress_callback(self, total_words):
        def progress_callback(event_type, *args):
            if event_type == 'progress':
                tested, found = args
                if tested % 10 == 0 or tested == total_words:
                    self.console.print_progress(self.completed, self.total_domains, tested, total_words)
            elif event_type == 'wildcard_detected':
                wildcard_ips = args[0]
                self.console.print_info(f"Wildcard DNS detected! IPs: {', '.join(wildcard_ips)}")
                self.console.print_info("Results will be filtered to exclude wildcard responses")
            elif event_type == 'found':
                subdomain, ip = args
                self.console.print_found_subdomain(subdomain, ip)
        return progress_callback

    @staticmethod
    def save_subdomains(subdomains, output_file):
        if not subdomains:
            return
            
        with open(output_file, "a", encoding="utf-8") as f:
            f.write("\n".join(sorted(subdomains)) + "\n")

    def process_domain(self, domain, output_file, total_words):
        if not DomainValidator.is_valid_domain(domain):
            self.completed += 1
            return set()

        self.console.print_domain_start(domain)
        progress_callback = self._create_progress_callback(total_words)
        
        try:
            subdomains = self.bruteforcer.bruteforce_domain(domain, progress_callback)
            self.console.update_domain_stats(domain, len(subdomains))
            self.console.print_domain_complete(domain, len(subdomains))
            self.save_subdomains(subdomains, output_file)
        except Exception as e:
            self.console.print_error(f"Error processing domain {domain}: {str(e)}")
            subdomains = set()

        self.completed += 1
        return subdomains

    def run(self, domains, output_file, max_concurrent_domains=1):
        if not domains:
            self.console.print_error("No valid domains provided")
            return set()

        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        
        try:
            total_words = self.bruteforcer.load_wordlist()
            self.console.print_info(f"Loaded wordlist with {total_words} entries")
        except Exception as e:
            self.console.print_error(f"Failed to load wordlist: {str(e)}")
            return set()

        self.completed = 0
        self.total_domains = len(domains)
        all_subdomains = set()

        self.console.print_info(f"Starting subdomain bruteforce for {len(domains)} domain(s)")
        self.console.print_info(f"Using {self.bruteforcer.max_workers} concurrent threads per domain")

        with self.cursor_manager:
            futures = []
            with ThreadPoolExecutor(max_workers=max_concurrent_domains) as executor:
                futures = [
                    executor.submit(self.process_domain, domain, output_file, total_words)
                    for domain in domains
                ]
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        all_subdomains.update(result)
                    except Exception as e:
                        self.console.print_error(f"Error processing domain: {str(e)}")

            self.console.print_final_summary(output_file)
            return all_subdomains


def main():
    domains = []
    
    input_type = get_input("Select input mode", "choice",
                           choices=["Manual", "File"])

    if input_type == "Manual":
        domain_input = get_input("Enter domain(s)")
        domains = [d.strip() for d in domain_input.split(',') 
                  if DomainValidator.is_valid_domain(d.strip())]
        default_output = f"{domains[0]}_subdomains_bruteforce.txt" if domains else "subdomains_bruteforce.txt"
    else:
        file_path = get_input("Enter filename", "file")
        try:
            with open(file_path, 'r') as f:
                domains = [d.strip() for d in f.readlines() 
                          if DomainValidator.is_valid_domain(d.strip())]
            default_output = f"{file_path.rsplit('.', 1)[0]}_subdomains_bruteforce.txt"
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return

    if not domains:
        print("No valid domains found!")
        return

    output_file = get_input("Enter output filename", default=default_output)

    use_custom_wordlist = get_confirm(" Use custom wordlist?")

    wordlist_path = get_input("Enter wordlist path", "file") if use_custom_wordlist else None

    max_workers = int(get_input("Max concurrent threads per domain", 
                               default="50"))
    dns_timeout = int(get_input("DNS timeout in seconds", 
                               default="3"))
    enable_wildcard_filtering = get_confirm(" Enable wildcard filtering?")

    subbrute = SubBrute(
        wordlist_path=wordlist_path,
        max_workers=max_workers,
        dns_timeout=dns_timeout,
        enable_wildcard_filtering=enable_wildcard_filtering
    )
    
    subbrute.run(domains, output_file, max_concurrent_domains=1)
