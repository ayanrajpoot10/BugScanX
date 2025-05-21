from rich.console import Console


class IPLookupConsole(Console):
    def __init__(self):
        super().__init__()
        self.total_domains = 0
        self.ip_stats = {}

    def print_ip_start(self, ip):
        self.print(f"[cyan]Processing: {ip}[/cyan]")
    
    def update_ip_stats(self, ip, count):
        self.ip_stats[ip] = count
        self.total_domains += count
    
    def print_ip_complete(self, ip, count):
        self.print(f"[green]{ip}: {count} domains found[/green]")
    
    def print_final_summary(self, output_file):
        print("\r\033[K", end="")
        self.print(f"\n[green]Total: [bold]{self.total_domains}[/bold] domains found")
        self.print(f"[green]Results saved to {output_file}[/green]")

    def print_progress(self, current, total):
        self.print(f"Progress: {current} / {total}", end="\r")
    
    def print_error(self, message):
        self.print(f"[red]{message}[/red]")
