from rich.console import Console


class SubFinderConsole(Console):
    def __init__(self):
        super().__init__()
        self.total_subdomains = 0
        self.domain_stats = {}

    def print_domain_start(self, domain):
        self.print(f"[cyan]Processing: {domain}[/cyan]")
    
    def update_domain_stats(self, domain, count):
        self.domain_stats[domain] = count
        self.total_subdomains += count
    
    def print_domain_complete(self, domain, count):
        self.print(f"[green]{domain}: {count} subdomains found[/green]")
    
    def print_final_summary(self, output_file):
        print("\r\033[K", end="")
        self.print(f"\n[green]Total: [bold]{self.total_subdomains}[/bold] subdomains found")
        self.print(f"[green]Results saved to {output_file}[/green]")

    def print_progress(self, current, total):
        self.print(f"Progress: {current} / {total}", end="\r")
    
    def print_error(self, message):
        self.print(f"[red]{message}[/red]")
