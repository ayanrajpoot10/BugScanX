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

class IPLookupConsole:
    def __init__(self):
        self.total_domains = 0
        self.ip_stats = {}
        self.logger = Logger()
    
    def start_ip_scan(self, ip):
        self.logger.clear_line()
        console.print(f"[cyan] Processing: {ip}[/cyan]")
    
    def update_ip_stats(self, ip, count):
        self.ip_stats[ip] = count
        self.total_domains += count
    
    def print_ip_complete(self, ip, domains_count):
        self.logger.clear_line()
        console.print(f"[green] {ip}: {domains_count} domains found[/green]")
    
    def print_final_summary(self, output_file):
        console.print(f"\n[green] Total [bold]{self.total_domains}[/bold] domains found[/green]")
        console.print(f"[green] Results saved to {output_file}[/green]")
        
    def print_error(self, message):
        console.print(f"[bold red]✗ ERROR: {message}[/bold red]")
