import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from bugscanx.utils.common import get_input, is_cidr
from .sources import get_scrapers
from .utils import CursorManager, process_input, process_file
from .logger import IPLookupConsole


class IPLookup:
    def __init__(self):
        self.console = IPLookupConsole()
        self.cursor_manager = CursorManager()
        self.completed = 0

    def _fetch_from_source(self, source, ip):
        try:
            return source.fetch(ip)
        except Exception:
            return set()

    def _save_domains(self, domains, output_file):
        if domains:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write("\n".join(sorted(domains)) + "\n")

    def process_ip(self, ip, output_file, scrapers, total):
        self.console.print_ip_start(ip)
        self.console.print_progress(self.completed, total)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self._fetch_from_source, source, ip)
                for source in scrapers
            ]
            results = [f.result() for f in as_completed(futures)]

        domains = set().union(*results) if results else set()

        self.console.update_ip_stats(ip, len(domains))
        self.console.print_ip_complete(ip, len(domains))
        self._save_domains(domains, output_file)

        self.completed += 1
        self.console.print_progress(self.completed, total)
        return domains

    def run(self, ips, output_file, scrapers=None):
        if not ips:
            self.console.print_error("No valid IPs provided")
            return

        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        self.completed = 0
        all_domains = set()
        total = len(ips)
        scrapers = scrapers or get_scrapers()
        
        with self.cursor_manager:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(self.process_ip, ip, output_file, scrapers, total)
                    for ip in ips
                ]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        all_domains.update(result)
                    except Exception as e:
                        self.console.print_error(f"Error processing IP: {str(e)}")

            self.console.print_final_summary(output_file)
            return all_domains


def main():
    ips = []
    input_type = get_input("Select input mode", "choice",
                          choices=["Manual", "File"])

    if input_type == "Manual":
        ip_input = get_input("Enter IP or CIDR", validators=[is_cidr])
        ips.extend(process_input(ip_input))
        default_output = f"{ip_input}_domains.txt".replace("/", "-")
    else:
        file_path = get_input("Enter filename", "file")
        ips.extend(process_file(file_path))
        default_output = f"{file_path.rsplit('.', 1)[0]}_domains.txt"

    output_file = get_input("Enter output filename", default=default_output)
    iplookup = IPLookup()
    iplookup.run(ips, output_file)
