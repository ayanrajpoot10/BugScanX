from threading import RLock
from rich.console import Console

console = Console()

class Logger:
    def __init__(self):
        self._lock = RLock()

    def clear_line(self):
        with self._lock:
            print("\033[2K\r", end='', flush=True)

    def replace(self, message):
        with self._lock:
            print(f"{message}", end='', flush=True)

class SubFinderConsole:
    def __init__(self):
        self.total_subdomains = 0
        self.domain_stats = {}
        self.logger = Logger()
    
    def start_domain_scan(self, domain):
        self.logger.clear_line()
        console.print(f"[cyan] Processing: {domain}[/cyan]")
    
    def update_domain_stats(self, domain, count):
        self.domain_stats[domain] = count
        self.total_subdomains += count
    
    def print_domain_complete(self, domain, subdomains_count):
        self.logger.clear_line()
        console.print(f"[green] {domain}: {subdomains_count} subdomains found[/green]")
    
    def print_final_summary(self, output_file):
        console.print(f"\n[green] Total: [bold]{self.total_subdomains}[/bold] subdomains found[/green]")
        console.print(f"[green] Results saved to {output_file}[/green]")

    def show_progress(self, current, total):
        progress_message = f" progress: [{current}/{total}]\r"
        self.logger.replace(progress_message)
    
    def print(self, message):
        self.logger.clear_line()
        console.print(message)
    
    def print_error(self, message):
        self.logger.clear_line()
        console.print(f"[red] {message}[/red]")
