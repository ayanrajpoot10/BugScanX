from rich.console import Console

class SubBruteConsole(Console):
    def __init__(self):
        super().__init__()
        self.total_subdomains = 0
        self.domain_stats = {}

    def print_domain_start(self, domain):
        print(f"\r\033[K", end="")
        self.print(f"[cyan]Processing: {domain}[/cyan]")
    
    def update_domain_stats(self, domain, count):
        self.domain_stats[domain] = count
        self.total_subdomains += count
    
    def print_domain_complete(self, domain, count):
        print(f"\r\033[K", end="")
        self.print(f"[green]{domain}: {count} subdomains found[/green]")
    
    def print_final_summary(self, output_file):
        print("\r\033[K", end="")
        self.print(f"\n[green]Total: [bold]{self.total_subdomains}[/bold] subdomains found")
        self.print(f"[green]Results saved to {output_file}[/green]")

    def print_progress(self, current_domain, total_domains, tested_words, total_words):
        wordlist_percent = (tested_words / total_words) * 100 if total_words > 0 else 0
        domain_percent = (current_domain / total_domains) * 100 if total_domains > 0 else 0
        
        print(f"\rDomain {current_domain}/{total_domains} ({domain_percent:.1f}%) | "
              f"{tested_words}/{total_words} words ({wordlist_percent:.1f}%)", end="", flush=True)
    
    def print_error(self, message):
        print(f"\r\033[K", end="")
        self.print(f"[red]{message}[/red]")
        
    def print_info(self, message):
        print(f"\r\033[K", end="")
        self.print(f"[blue]{message}[/blue]")
    
    def print_found_subdomain(self, subdomain, ip):
        print(f"\r\033[K", end="")
        self.print(f"[yellow]Found:[/yellow] [bold]{subdomain}[/bold] -> [dim]{ip}[/dim]")
