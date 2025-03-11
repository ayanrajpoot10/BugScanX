import dns.resolver
import dns.reversename
from rich import print

from bugscanx.utils import get_input

def resolve_and_print(domain, record_type):
    print(f"\n[green] {record_type} Records:[/green]")
    try:
        answers = dns.resolver.resolve(domain, record_type)
        found = False
        for answer in answers:
            found = True
            if record_type == 'MX':
                print(f"[cyan]- {answer.exchange} (priority: {answer.preference})[/cyan]")
            else:
                print(f"[cyan]- {answer.to_text()}[/cyan]")
        if not found:
            print(f"[yellow] No {record_type} records found[/yellow]")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        print(f"[yellow] No {record_type} records found[/yellow]")
    except Exception as e:
        print(f"[yellow]Warning: Error fetching {record_type} record: {str(e)}[/yellow]")

def nslookup(domain):
    print(f"[cyan]\n Performing NSLOOKUP for: {domain}[/cyan]")
    
    # Process each record type sequentially
    record_types = ['A', 'CNAME', 'MX', 'NS', 'TXT']
    for record_type in record_types:
        resolve_and_print(domain, record_type)

def dns_main():
    domain = get_input("Enter the domain to lookup")
    if not domain:
        print("[red] Please enter a valid domain.[/red]")
        return
    try:
        nslookup(domain)
    except Exception as e:
        print(f"[red]An error occurred during DNS lookup: {str(e)}[/red]")
