import os
from bugscanx.utils.utils import get_input
from .subfinder_console import SubFinderConsole
from .subfinder_sources import get_all_sources, get_bulk_sources
from .subfinder_utils import is_valid_domain
from .subdomain_finder import SubdomainFinder

def main():
    console = SubFinderConsole()
    
    domains = []
    input_type = get_input("Select input type", "choice", 
                         choices=["single domain", "bulk domains"])
    
    if input_type == "single domain":
        domain = get_input("Enter domain")
        if is_valid_domain(domain):
            domains = [domain]
            sources = get_all_sources()
            default_output = f"{domain}_subdomains.txt"
        else:
            console.print_error(f"Invalid domain: {domain}")
            return
    else:
        file_path = get_input("Enter filename", "file")
        with open(file_path, 'r') as f:
            domains = [d.strip() for d in f if is_valid_domain(d.strip())]
        sources = get_bulk_sources()
        default_output = f"{file_path.rsplit('.', 1)[0]}_subdomains.txt"

    if not domains:
        console.print_error("No valid domains provided")
        return

    output_file = get_input("Enter output filename", default=default_output)
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)

    finder = SubdomainFinder(console)
    finder.find_subdomains(domains, output_file, sources)
